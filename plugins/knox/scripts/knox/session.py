from __future__ import annotations

import json
import hashlib
import re
import secrets
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import config


ALLOWED_TTLS = {15, 60, 180}


@dataclass
class Session:
    token: str
    issued_at: int
    expires_at: int
    request_label: str
    scopes: list[str]
    key_bindings: dict[str, str]
    client_hint: str | None = None


@dataclass
class ProxyToken:
    token: str
    agent_id: str
    issued_at: int
    expires_at: int
    request_label: str
    scopes: list[str]
    key_bindings: dict[str, str]
    client_hint: str | None = None


@dataclass
class PendingChallenge:
    challenge_token: str
    code_hash: str
    expires_at: int
    request_label: str
    scopes: list[str]
    ttl_minutes: int
    client_hint: str | None = None


def _now() -> int:
    return int(time.time())


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def _hash_token(token: str) -> str:
    return hashlib.sha256(f"knox-session:{token}".encode()).hexdigest()


def _hash_challenge_token(token: str) -> str:
    return hashlib.sha256(f"knox-challenge:{token}".encode()).hexdigest()


def _hash_proxy_token(token: str) -> str:
    return hashlib.sha256(f"knox-proxy:{token}".encode()).hexdigest()


def _is_sha256_hex(value: str) -> bool:
    return bool(re.fullmatch(r"[0-9a-f]{64}", value))


def _serialize_bindings(bindings: dict[str, str]) -> str:
    return json.dumps(dict(sorted(bindings.items())), sort_keys=True)


def _deserialize_bindings(raw: str | None) -> dict[str, str]:
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {}
    if not isinstance(parsed, dict):
        return {}
    normalized: dict[str, str] = {}
    for key, value in parsed.items():
        if isinstance(key, str) and isinstance(value, str) and key and value:
            normalized[key] = value
    return normalized


class StoreError(RuntimeError):
    pass


class SessionStore:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or config.KNOX_STATE_DB
        config.ensure_directory(self.db_path.parent)
        self._init_db()

    def _secure_db_files(self) -> None:
        for path in (
            self.db_path,
            self.db_path.with_name(f"{self.db_path.name}-wal"),
            self.db_path.with_name(f"{self.db_path.name}-shm"),
        ):
            if path.exists():
                try:
                    path.chmod(0o600)
                except OSError:
                    pass

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        self._secure_db_files()
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    token TEXT PRIMARY KEY,
                    issued_at INTEGER NOT NULL,
                    expires_at INTEGER NOT NULL,
                    request_label TEXT NOT NULL,
                    client_hint TEXT,
                    scopes_json TEXT NOT NULL,
                    revoked INTEGER NOT NULL DEFAULT 0
                );
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS challenges (
                    token TEXT PRIMARY KEY,
                    code_hash TEXT NOT NULL,
                    expires_at INTEGER NOT NULL,
                    request_label TEXT NOT NULL,
                    client_hint TEXT,
                    scopes_json TEXT NOT NULL,
                    ttl_minutes INTEGER NOT NULL
                );
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS idempotency (
                    token_hash TEXT NOT NULL,
                    idempotency_key TEXT NOT NULL,
                    used_at INTEGER NOT NULL,
                    result_json TEXT,
                    PRIMARY KEY (token_hash, idempotency_key),
                    FOREIGN KEY(token_hash) REFERENCES sessions(token_hash) ON DELETE CASCADE
                );
                """
            )
            self._migrate_schema(conn)
            legacy_purged = self._purge_legacy_plaintext_tokens(conn)
            conn.commit()
            if legacy_purged:
                conn.execute("VACUUM;")
            self._secure_db_files()

    def _migrate_schema(self, conn: sqlite3.Connection) -> None:
        for table in ("sessions", "challenges", "idempotency"):
            rows = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name = ?;",
                (table,),
            ).fetchall()
            if not rows:
                continue

            columns = [row[1] for row in conn.execute(f"PRAGMA table_info({table});").fetchall()]
            if "token_hash" not in columns and "token" in columns:
                conn.execute(f"ALTER TABLE {table} RENAME COLUMN token TO token_hash;")

        session_columns = [row[1] for row in conn.execute("PRAGMA table_info(sessions);").fetchall()]
        if "key_bindings_json" not in session_columns:
            conn.execute("ALTER TABLE sessions ADD COLUMN key_bindings_json TEXT NOT NULL DEFAULT '{}'")

        table_names = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()}
        if "proxy_tokens" not in table_names:
            conn.execute(
                """
                CREATE TABLE proxy_tokens (
                    token_hash TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    issued_at INTEGER NOT NULL,
                    expires_at INTEGER NOT NULL,
                    request_label TEXT NOT NULL,
                    client_hint TEXT,
                    scopes_json TEXT NOT NULL,
                    key_bindings_json TEXT NOT NULL DEFAULT '{}',
                    revoked INTEGER NOT NULL DEFAULT 0
                );
                """
            )

        if "idempotency" in table_names:
            idempo_columns = [row[1] for row in conn.execute("PRAGMA table_info(idempotency);").fetchall()]
            if "token_hash" not in idempo_columns and "token" in idempo_columns:
                conn.execute("ALTER TABLE idempotency RENAME COLUMN token TO token_hash;")

    def _purge_legacy_plaintext_tokens(self, conn: sqlite3.Connection) -> bool:
        purged = False
        for table in ("idempotency", "challenges", "sessions"):
            columns = [row[1] for row in conn.execute(f"PRAGMA table_info({table});").fetchall()]
            if "token_hash" not in columns:
                continue
            values = [row[0] for row in conn.execute(f"SELECT token_hash FROM {table};").fetchall()]
            if any(isinstance(value, str) and not _is_sha256_hex(value) for value in values):
                conn.execute(f"DELETE FROM {table};")
                purged = True
        return purged

    def prune_expired(self) -> None:
        now = _now()
        with self._connect() as conn:
            conn.execute("DELETE FROM sessions WHERE expires_at < ?;", (now,))
            conn.execute("DELETE FROM challenges WHERE expires_at < ?;", (now,))
            conn.execute("DELETE FROM idempotency WHERE token_hash NOT IN (SELECT token_hash FROM sessions);")
            conn.execute("DELETE FROM proxy_tokens WHERE expires_at < ?;", (now,))

    def create_challenge(
        self,
        challenge_token: str,
        code: str,
        request_label: str,
        scopes: list[str],
        ttl_minutes: int,
        client_hint: str | None = None,
        ttl_seconds: int | None = None,
    ) -> PendingChallenge:
        expires = _now() + (ttl_seconds or 90)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO challenges
                (token_hash, code_hash, expires_at, request_label, client_hint, scopes_json, ttl_minutes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _hash_challenge_token(challenge_token),
                    _hash_code(code),
                    expires,
                    request_label,
                    client_hint,
                    "\n".join(sorted(scopes)),
                    ttl_minutes,
                ),
            )
        return PendingChallenge(
            challenge_token=challenge_token,
            code_hash=_hash_code(code),
            expires_at=expires,
            request_label=request_label,
            scopes=scopes,
            ttl_minutes=ttl_minutes,
            client_hint=client_hint,
        )

    def verify_challenge(
        self,
        challenge_token: str,
        code: str,
    ) -> PendingChallenge | None:
        now = _now()
        with self._connect() as conn:
            row = conn.execute(
                "SELECT token_hash, code_hash, expires_at, request_label, client_hint, scopes_json, ttl_minutes "
                "FROM challenges WHERE token_hash = ? AND expires_at >= ?;",
                (_hash_challenge_token(challenge_token), now),
            ).fetchone()
            if not row:
                return None
            _, code_hash, expires_at, request_label, client_hint, scopes_json, ttl_minutes = row
            if code_hash != _hash_code(code):
                return None
            conn.execute("DELETE FROM challenges WHERE token_hash = ?;", (_hash_challenge_token(challenge_token),))
            return PendingChallenge(
                challenge_token=challenge_token,
                code_hash=code_hash,
                expires_at=expires_at,
                request_label=request_label,
                scopes=scopes_json.split("\n") if scopes_json else [],
                ttl_minutes=ttl_minutes,
                client_hint=client_hint,
            )

    def issue_session(
        self,
        scopes: list[str],
        ttl_minutes: int,
        request_label: str,
        client_hint: str | None = None,
        key_bindings: dict[str, str] | None = None,
    ) -> Session:
        if ttl_minutes not in ALLOWED_TTLS:
            raise StoreError("ttl_minutes must be one of: 15, 60, 180")
        issued_at = _now()
        expires_at = issued_at + (ttl_minutes * 60)
        token = secrets.token_urlsafe(24)
        bindings = key_bindings or {}
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO sessions
                (token_hash, issued_at, expires_at, request_label, client_hint, scopes_json, key_bindings_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _hash_token(token),
                    issued_at,
                    expires_at,
                    request_label,
                    client_hint,
                    "\n".join(sorted(scopes)),
                    _serialize_bindings(bindings),
                ),
            )
        return Session(
            token=token,
            issued_at=issued_at,
            expires_at=expires_at,
            request_label=request_label,
            client_hint=client_hint,
            scopes=scopes,
            key_bindings=bindings,
        )

    def issue_proxy_token(
        self,
        agent_id: str,
        scopes: list[str],
        ttl_minutes: int,
        request_label: str,
        client_hint: str | None = None,
        key_bindings: dict[str, str] | None = None,
    ) -> ProxyToken:
        if ttl_minutes not in ALLOWED_TTLS:
            raise StoreError("ttl_minutes must be one of: 15, 60, 180")
        issued_at = _now()
        expires_at = issued_at + (ttl_minutes * 60)
        token = secrets.token_urlsafe(24)
        bindings = key_bindings or {}
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO proxy_tokens
                (token_hash, agent_id, issued_at, expires_at, request_label, client_hint, scopes_json, key_bindings_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _hash_proxy_token(token),
                    agent_id,
                    issued_at,
                    expires_at,
                    request_label,
                    client_hint,
                    "\n".join(sorted(scopes)),
                    _serialize_bindings(bindings),
                ),
            )
        return ProxyToken(
            token=token,
            agent_id=agent_id,
            issued_at=issued_at,
            expires_at=expires_at,
            request_label=request_label,
            client_hint=client_hint,
            scopes=scopes,
            key_bindings=bindings,
        )

    def get_session(self, token: str) -> Session | None:
        now = _now()
        with self._connect() as conn:
            row = conn.execute(
                "SELECT token_hash, issued_at, expires_at, request_label, client_hint, scopes_json, key_bindings_json, revoked "
                "FROM sessions WHERE token_hash = ? AND revoked = 0;",
                (_hash_token(token),),
            ).fetchone()
            if not row:
                return None
            (
                _token_hash,
                issued_at,
                expires_at,
                request_label,
                client_hint,
                scopes_json,
                key_bindings_json,
                revoked,
            ) = row
            if revoked or expires_at < now:
                return None
            return Session(
                token=token,
                issued_at=int(issued_at),
                expires_at=int(expires_at),
                request_label=request_label,
                client_hint=client_hint,
                scopes=scopes_json.split("\n") if scopes_json else [],
                key_bindings=_deserialize_bindings(key_bindings_json),
            )

    def get_proxy_token(self, token: str) -> ProxyToken | None:
        now = _now()
        with self._connect() as conn:
            row = conn.execute(
                "SELECT token_hash, agent_id, issued_at, expires_at, request_label, client_hint, scopes_json, key_bindings_json, revoked "
                "FROM proxy_tokens WHERE token_hash = ? AND revoked = 0;",
                (_hash_proxy_token(token),),
            ).fetchone()
            if not row:
                return None
            (
                _token_hash,
                agent_id,
                issued_at,
                expires_at,
                request_label,
                client_hint,
                scopes_json,
                key_bindings_json,
                revoked,
            ) = row
            if revoked or expires_at < now:
                return None
            return ProxyToken(
                token=token,
                agent_id=agent_id,
                issued_at=int(issued_at),
                expires_at=int(expires_at),
                request_label=request_label,
                client_hint=client_hint,
                scopes=scopes_json.split("\n") if scopes_json else [],
                key_bindings=_deserialize_bindings(key_bindings_json),
            )

    def revoke_proxy_token(self, token: str) -> bool:
        with self._connect() as conn:
            cursor = conn.execute("UPDATE proxy_tokens SET revoked = 1 WHERE token_hash = ?;", (_hash_proxy_token(token),))
            return cursor.rowcount > 0

    def proxy_token_status(self, token: str) -> dict[str, Any] | None:
        proxy = self.get_proxy_token(token)
        if not proxy:
            return None
        now = _now()
        return {
            "active": True,
            "agent_id": proxy.agent_id,
            "token": proxy.token,
            "issued_at": proxy.issued_at,
            "expires_at": proxy.expires_at,
            "request_label": proxy.request_label,
            "client_hint": proxy.client_hint,
            "scopes": proxy.scopes,
            "key_bindings": proxy.key_bindings,
            "seconds_left": max(0, proxy.expires_at - now),
        }

    def revoke_session(self, token: str) -> bool:
        with self._connect() as conn:
            cursor = conn.execute("UPDATE sessions SET revoked = 1 WHERE token_hash = ?;", (_hash_token(token),))
            return cursor.rowcount > 0

    def session_status(self, token: str) -> dict[str, Any] | None:
        session = self.get_session(token)
        if not session:
            return None
        now = _now()
        return {
            "active": True,
            "token": session.token,
            "issued_at": session.issued_at,
            "expires_at": session.expires_at,
            "request_label": session.request_label,
            "client_hint": session.client_hint,
            "scopes": session.scopes,
            "key_bindings": session.key_bindings,
            "seconds_left": max(0, session.expires_at - now),
        }

    def mark_idempotent(
        self,
        token: str,
        idempotency_key: str,
        result_json: str,
    ) -> bool:
        now = _now()
        with self._connect() as conn:
            try:
                conn.execute(
                    "INSERT INTO idempotency (token_hash, idempotency_key, used_at, result_json) VALUES (?, ?, ?, ?);",
                    (_hash_token(token), idempotency_key, now, result_json),
                )
                return True
            except sqlite3.IntegrityError:
                return False

    def read_idempotent(self, token: str, idempotency_key: str) -> str | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT result_json FROM idempotency WHERE token_hash = ? AND idempotency_key = ?;",
                (_hash_token(token), idempotency_key),
            ).fetchone()
            return row[0] if row else None
