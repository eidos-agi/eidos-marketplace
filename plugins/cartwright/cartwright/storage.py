from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timezone

from .models import CanonicalItem
from .constants import DEFAULT_DB_PATH


@dataclass
class GroceryPlanRow:
    item: CanonicalItem
    list_id: int | None = None
    list_source: str | None = None


class CartwrightStore:
    def __init__(self, db_path: str | None = None) -> None:
        self.db_path = str(Path(db_path).expanduser()) if db_path else str(DEFAULT_DB_PATH)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _ts() -> str:
        return datetime.now(timezone.utc).isoformat()

    def initialize(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS shopping_profile (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    profile_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS shopping_lists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    source_ref TEXT,
                    active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS shopping_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    list_id INTEGER NOT NULL,
                    source TEXT NOT NULL,
                    raw_text TEXT NOT NULL,
                    normalized_name TEXT NOT NULL,
                    quantity TEXT NOT NULL,
                    unit TEXT,
                    brand_preference TEXT,
                    must_match_brand INTEGER NOT NULL DEFAULT 0,
                    category TEXT NOT NULL,
                    notes TEXT,
                    confidence REAL NOT NULL,
                    imported_via TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(list_id) REFERENCES shopping_lists(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS purchase_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    retailer TEXT,
                    receipt_date TEXT,
                    normalized_name TEXT NOT NULL,
                    quantity TEXT,
                    unit TEXT,
                    brand_preference TEXT,
                    notes TEXT,
                    confidence REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    raw_payload TEXT
                );
                CREATE TABLE IF NOT EXISTS source_connections (
                    source TEXT PRIMARY KEY,
                    last_checked_at TEXT,
                    status TEXT,
                    last_error TEXT,
                    metadata TEXT
                );
                CREATE TABLE IF NOT EXISTS export_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    list_id INTEGER,
                    export_format TEXT NOT NULL,
                    output_target TEXT,
                    created_at TEXT NOT NULL,
                    summary_json TEXT,
                    FOREIGN KEY(list_id) REFERENCES shopping_lists(id) ON DELETE SET NULL
                );
                """
            )
            conn.commit()

    def set_profile(self, profile: dict, source: str = "manual") -> None:
        now = self._ts()
        payload = json.dumps(profile or {}, sort_keys=True)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO shopping_profile (id, profile_json, created_at, updated_at)
                VALUES (1, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET profile_json=excluded.profile_json, updated_at=excluded.updated_at
                """,
                (payload, now, now),
            )
            conn.execute(
                "INSERT INTO source_connections(source, last_checked_at, status, metadata) VALUES (?, ?, ?, ?)\n"
                "ON CONFLICT(source) DO UPDATE SET last_checked_at=excluded.last_checked_at, status=excluded.status, metadata=excluded.metadata",
                (source, now, "imported", json.dumps({"profile_update": True}, sort_keys=True)),
            )
            conn.commit()

    def remember_source_connection(
        self,
        source: str,
        status: str = "ready",
        metadata: dict | None = None,
        last_error: str | None = None,
    ) -> None:
        now = self._ts()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO source_connections(source, last_checked_at, status, last_error, metadata)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(source) DO UPDATE SET
                    last_checked_at=excluded.last_checked_at,
                    status=excluded.status,
                    last_error=excluded.last_error,
                    metadata=excluded.metadata
                """,
                (
                    source,
                    now,
                    status,
                    last_error,
                    json.dumps(metadata or {}, sort_keys=True),
                ),
            )
            conn.commit()

    def get_source_connection(self, source: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT source, last_checked_at, status, last_error, metadata
                FROM source_connections
                WHERE source = ?
                """,
                (source,),
            ).fetchone()
            if not row:
                return None
            payload = dict(row)
            metadata = payload.get("metadata")
            payload["metadata"] = json.loads(metadata) if metadata else {}
            return payload

    def get_profile(self) -> dict:
        with self._connect() as conn:
            row = conn.execute("SELECT profile_json FROM shopping_profile WHERE id = 1").fetchone()
            if not row:
                return {}
            return json.loads(row["profile_json"])

    def create_list(self, source: str, source_ref: str | None = None) -> int:
        now = self._ts()
        with self._connect() as conn:
            conn.execute("UPDATE shopping_lists SET active = 0 WHERE active = 1")
            cur = conn.execute(
                "INSERT INTO shopping_lists(source, source_ref, active, created_at) VALUES (?, ?, 1, ?)",
                (source, source_ref, now),
            )
            conn.commit()
            return int(cur.lastrowid)

    def import_items(
        self,
        source: str,
        items: list[CanonicalItem],
        source_ref: str | None = None,
    ) -> int:
        list_id = self.create_list(source=source, source_ref=source_ref)
        now = self._ts()
        if not items:
            return list_id
        with self._connect() as conn:
            for item in items:
                conn.execute(
                    """
                    INSERT INTO shopping_items(
                        list_id, source, raw_text, normalized_name, quantity, unit,
                        brand_preference, must_match_brand, category, notes, confidence, imported_via, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        list_id,
                        item.source,
                        item.raw_text,
                        item.normalized_name,
                        item.quantity,
                        item.unit,
                        item.brand_preference,
                        int(bool(item.must_match_brand)),
                        item.category,
                        item.notes,
                        item.confidence,
                        source,
                        now,
                    ),
                )
            conn.commit()
        return list_id

    def add_receipt_items(
        self,
        source: str,
        retailer: str | None,
        items: list[CanonicalItem],
        receipt_date: str | None,
        raw_payload: str | None = None,
    ) -> None:
        now = self._ts()
        with self._connect() as conn:
            for item in items:
                conn.execute(
                    """
                    INSERT INTO purchase_history(
                        source, retailer, receipt_date, normalized_name, quantity, unit, brand_preference,
                        notes, confidence, created_at, raw_payload
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        source,
                        retailer,
                        receipt_date,
                        item.normalized_name,
                        item.quantity,
                        item.unit,
                        item.brand_preference,
                        item.notes,
                        item.confidence,
                        now,
                        raw_payload,
                    ),
                )
            conn.execute(
                "INSERT OR REPLACE INTO source_connections(source, last_checked_at, status, metadata) VALUES (?, ?, ?, ?)",
                (source, now, "imported", json.dumps({"receipt_import_count": len(items)}, sort_keys=True)),
            )
            conn.commit()

    def _active_list(self, conn: sqlite3.Connection) -> sqlite3.Row | None:
        return conn.execute(
            """
            SELECT * FROM shopping_lists
            WHERE active = 1
            ORDER BY created_at DESC
            LIMIT 1
            """
        ).fetchone()

    def get_active_items(self) -> list[CanonicalItem]:
        with self._connect() as conn:
            row = self._active_list(conn)
            if not row:
                return []
            items = conn.execute(
                """
                SELECT source, raw_text, normalized_name, quantity, unit, brand_preference,
                       must_match_brand, category, notes, confidence
                FROM shopping_items
                WHERE list_id = ?
                ORDER BY id ASC
                """,
                (row["id"],),
            ).fetchall()
            return [
                CanonicalItem(
                    source=item["source"],
                    raw_text=item["raw_text"],
                    normalized_name=item["normalized_name"],
                    quantity=item["quantity"],
                    unit=item["unit"],
                    brand_preference=item["brand_preference"],
                    must_match_brand=bool(item["must_match_brand"]),
                    category=item["category"],
                    notes=item["notes"],
                    confidence=float(item["confidence"]),
                )
                for item in items
            ]

    def get_active_list_id(self) -> int | None:
        with self._connect() as conn:
            row = self._active_list(conn)
            return int(row["id"]) if row else None

    def get_active_list_with_metadata(self) -> list[dict[str, object]]:
        with self._connect() as conn:
            row = self._active_list(conn)
            if not row:
                return []
            return [
                dict(item)
                for item in conn.execute(
                    """
                    SELECT
                        si.id AS item_id,
                        sl.id AS list_id,
                        sl.source AS list_source,
                        sl.source_ref,
                        sl.created_at AS list_created_at,
                        si.source,
                        si.raw_text,
                        si.normalized_name,
                        si.quantity,
                        si.unit,
                        si.brand_preference,
                        si.must_match_brand,
                        si.category,
                        si.notes,
                        si.confidence
                    FROM shopping_lists sl
                    JOIN shopping_items si ON si.list_id = sl.id
                    WHERE sl.id = ?
                    ORDER BY si.id
                    """,
                    (row["id"],),
                ).fetchall()
            ]

    def get_purchase_history(self, days: int = 180) -> list[CanonicalItem]:
        # Keep this bounded by time window for recent-staple signals only.
        cutoff = None
        if days:
            cutoff = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
            # SQLite date math handled in query.
        with self._connect() as conn:
            if days > 0:
                rows = conn.execute(
                    """
                    SELECT source, COALESCE(retailer,'') as source_name, normalized_name, quantity, unit,
                           brand_preference, notes, confidence
                    FROM purchase_history
                    WHERE date(created_at) >= date(?, '-{} days')
                    ORDER BY created_at DESC
                    """.format(days),
                    (cutoff,),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT source, COALESCE(retailer,'') as source_name, normalized_name, quantity, unit,
                           brand_preference, notes, confidence
                    FROM purchase_history
                    ORDER BY created_at DESC
                    """
                ).fetchall()
            return [
                CanonicalItem(
                    source=row["source"] or "gmail",
                    raw_text=f"{row['source_name']}: {row['normalized_name']}",
                    normalized_name=row["normalized_name"],
                    quantity=row["quantity"] or "1",
                    unit=row["unit"],
                    brand_preference=row["brand_preference"],
                    must_match_brand=False,
                    category="uncategorized",
                    notes=row["notes"],
                    confidence=float(row["confidence"] or 0.7),
                )
                for row in rows
            ]

    def get_recent_staples(self, days: int = 180, min_count: int = 2, top_n: int = 10) -> list[str]:
        with self._connect() as conn:
            cutoff = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
            rows = conn.execute(
                """
                SELECT normalized_name, COUNT(*) as cnt
                FROM purchase_history
                WHERE date(created_at) >= date(?, '-{} days')
                GROUP BY normalized_name
                HAVING COUNT(*) >= ?
                ORDER BY cnt DESC, normalized_name ASC
                LIMIT ?
                """.format(days),
                (cutoff, min_count, top_n),
            ).fetchall()
            return [row["normalized_name"] for row in rows]

    def log_export(self, list_id: int | None, export_format: str, output_target: str | None, summary: dict) -> None:
        now = self._ts()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO export_log(list_id, export_format, output_target, created_at, summary_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (list_id, export_format, output_target, now, json.dumps(summary, sort_keys=True)),
            )
            conn.commit()
