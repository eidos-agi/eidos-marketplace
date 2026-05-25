from pathlib import Path
import sqlite3
import stat

from scripts.knox.session import SessionStore, StoreError


def _store(tmp_path: Path) -> SessionStore:
    return SessionStore(tmp_path / "state.sqlite")


def test_issue_and_read_session(tmp_path: Path):
    store = _store(tmp_path)
    created = store.issue_session(scopes=["github:list_repos"], ttl_minutes=15, request_label="test")
    assert created.token
    assert created.expires_at == created.issued_at + 900
    assert store.get_session(created.token) is not None


def test_session_scope_and_ttl_validation(tmp_path: Path):
    # use an isolated database path
    store = SessionStore(tmp_path / "state.sqlite")
    try:
        store.issue_session(scopes=["github:list_repos"], ttl_minutes=99, request_label="bad-ttl")
        assert False, "Expected invalid ttl"
    except StoreError:
        assert True


def test_revoke_and_expired_behavior(tmp_path: Path):
    store = _store(tmp_path)
    created = store.issue_session(scopes=["github:list_repos"], ttl_minutes=15, request_label="revoke")
    assert store.revoke_session(created.token)
    assert store.get_session(created.token) is None

    active = store.issue_session(scopes=["github:list_repos"], ttl_minutes=15, request_label="active")
    status = store.session_status(active.token)
    assert status is not None and status["active"]


def test_challenge_lifecycle(tmp_path: Path):
    store = _store(tmp_path)
    token = "challenge-token"
    code = "123456"
    pending = store.create_challenge(token, code, "pending", ["github:list_repos"], 15)
    assert pending.challenge_token == token
    assert store.verify_challenge(token, "wrong") is None
    accepted = store.verify_challenge(token, code)
    assert accepted is not None
    assert accepted.ttl_minutes == 15
    # one-time use
    assert store.verify_challenge(token, code) is None


def test_idempotency_storage(tmp_path: Path):
    store = _store(tmp_path)
    created = store.issue_session(scopes=["github:list_repos"], ttl_minutes=15, request_label="idempotent")
    assert store.mark_idempotent(created.token, "abc", '{"ok":true}')
    assert store.read_idempotent(created.token, "abc") == '{"ok":true}'
    assert not store.mark_idempotent(created.token, "abc", '{"ok":false}')


def test_session_tokens_are_hashed_at_rest(tmp_path: Path):
    db_path = tmp_path / "state.sqlite"
    store = SessionStore(db_path)
    created = store.issue_session(scopes=["github:list_repos"], ttl_minutes=15, request_label="hashed")

    with sqlite3.connect(db_path) as conn:
        row = conn.execute("SELECT token_hash FROM sessions").fetchone()

    assert row is not None
    assert row[0] != created.token
    assert created.token not in db_path.read_bytes().decode("utf-8", errors="ignore")


def test_issue_and_revoke_proxy_token(tmp_path: Path):
    store = SessionStore(tmp_path / "state.sqlite")
    created = store.issue_proxy_token(
        agent_id="agent-1",
        scopes=["github:list_repos"],
        ttl_minutes=15,
        request_label="proxy",
    )
    assert created.token
    assert created.agent_id == "agent-1"
    assert created.expires_at == created.issued_at + 900
    assert store.get_proxy_token(created.token) is not None
    assert store.revoke_proxy_token(created.token)
    assert store.get_proxy_token(created.token) is None


def test_proxy_tokens_are_stored_hashed(tmp_path: Path):
    db_path = tmp_path / "state.sqlite"
    store = SessionStore(db_path)
    created = store.issue_proxy_token(
        agent_id="agent-2",
        scopes=["github:list_repos"],
        ttl_minutes=15,
        request_label="proxy-hash",
    )

    with sqlite3.connect(db_path) as conn:
        row = conn.execute("SELECT token_hash FROM proxy_tokens").fetchone()

    assert row is not None
    assert row[0] != created.token
    assert created.token not in db_path.read_bytes().decode("utf-8", errors="ignore")


def test_session_store_files_are_private(tmp_path: Path):
    db_path = tmp_path / "state.sqlite"
    store = SessionStore(db_path)
    store.issue_session(scopes=["github:list_repos"], ttl_minutes=15, request_label="permissions")

    for path in [db_path, db_path.with_name("state.sqlite-wal"), db_path.with_name("state.sqlite-shm")]:
        if path.exists():
            assert stat.S_IMODE(path.stat().st_mode) == 0o600


def test_legacy_plaintext_tokens_are_purged_and_vacuumed(tmp_path: Path):
    db_path = tmp_path / "state.sqlite"
    legacy_token = "legacy-plaintext-token"
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE sessions (
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
            CREATE TABLE challenges (
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
            CREATE TABLE idempotency (
                token TEXT NOT NULL,
                idempotency_key TEXT NOT NULL,
                used_at INTEGER NOT NULL,
                result_json TEXT,
                PRIMARY KEY (token, idempotency_key)
            );
            """
        )
        conn.execute(
            "INSERT INTO sessions (token, issued_at, expires_at, request_label, scopes_json) VALUES (?, 1, 9999999999, 'legacy', 'github:list_repos');",
            (legacy_token,),
        )
        conn.execute(
            "INSERT INTO challenges (token, code_hash, expires_at, request_label, scopes_json, ttl_minutes) VALUES (?, 'hash', 9999999999, 'legacy', 'github:list_repos', 15);",
            ("legacy-challenge-token",),
        )
        conn.execute(
            "INSERT INTO idempotency (token, idempotency_key, used_at, result_json) VALUES (?, 'k', 1, '{}');",
            (legacy_token,),
        )

    SessionStore(db_path)

    with sqlite3.connect(db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM challenges").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM idempotency").fetchone()[0] == 0
        assert "token_hash" in [row[1] for row in conn.execute("PRAGMA table_info(sessions)").fetchall()]

    db_text = db_path.read_bytes().decode("utf-8", errors="ignore")
    assert legacy_token not in db_text
    assert "legacy-challenge-token" not in db_text
