from __future__ import annotations

import json
from pathlib import Path
from threading import RLock
from typing import Any

from naviqra.models import Booking, MemoryRecord, new_id
from naviqra.database import Database


class SQLiteStore:
    """Small durable store; SQLite is the default adapter, not a hard-coded requirement."""

    def __init__(self, path: str | Path = "naviqra.db", *, initialize: bool = True) -> None:
        self.path = str(path)
        self.database = Database(self.path)
        self._lock = RLock()
        if initialize:
            self._initialize()

    def _connect(self):
        return self.database.connect()

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS memories (
              id TEXT PRIMARY KEY, traveler_id TEXT NOT NULL, kind TEXT NOT NULL,
              key TEXT NOT NULL, value_json TEXT NOT NULL, created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_memories_traveler ON memories(traveler_id);
            CREATE TABLE IF NOT EXISTS bookings (
              id TEXT PRIMARY KEY, trip_id TEXT NOT NULL, provider TEXT NOT NULL,
              item_type TEXT NOT NULL, item_id TEXT NOT NULL, amount REAL NOT NULL,
              currency TEXT NOT NULL, status TEXT NOT NULL, idempotency_key TEXT UNIQUE NOT NULL,
              created_at TEXT NOT NULL, approved_by TEXT
            );
            """)

    def check(self) -> None:
        """Raise when the backing database cannot be queried."""
        self.database.check()
        with self._connect() as conn:
            conn.execute("SELECT 1 FROM memories LIMIT 1").fetchone()

    def add_memory(self, record: MemoryRecord) -> MemoryRecord:
        with self._lock, self._connect() as conn:
            conn.execute(
                "INSERT INTO memories VALUES (?, ?, ?, ?, ?, ?)",
                (record.id, record.traveler_id, record.kind, record.key,
                 json.dumps(record.value), record.created_at.isoformat()),
            )
        return record

    def get_memories(self, traveler_id: str) -> list[MemoryRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM memories WHERE traveler_id=? ORDER BY created_at DESC",
                (traveler_id,),
            ).fetchall()
        return [MemoryRecord(id=r["id"], traveler_id=r["traveler_id"], kind=r["kind"],
                             key=r["key"], value=json.loads(r["value_json"]),
                             created_at=r["created_at"]) for r in rows]

    def create_booking(self, booking: Booking) -> Booking:
        with self._lock, self._connect() as conn:
            conn.execute(
                "INSERT INTO bookings VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (booking.id, booking.trip_id, booking.provider, booking.item_type,
                 booking.item_id, booking.amount, booking.currency, booking.status.value,
                 booking.idempotency_key, booking.created_at.isoformat(), booking.approved_by),
            )
        return booking

    def get_booking(self, booking_id: str) -> Booking | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM bookings WHERE id=?", (booking_id,)).fetchone()
        return self._booking_from_row(row) if row else None

    def get_booking_by_key(self, key: str) -> Booking | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM bookings WHERE idempotency_key=?", (key,)).fetchone()
        return self._booking_from_row(row) if row else None

    def update_booking(self, booking: Booking) -> Booking:
        with self._lock, self._connect() as conn:
            conn.execute("UPDATE bookings SET status=?, approved_by=? WHERE id=?",
                         (booking.status.value, booking.approved_by, booking.id))
        return booking

    @staticmethod
    def _booking_from_row(row: Any) -> Booking:
        return Booking(id=row["id"], trip_id=row["trip_id"], provider=row["provider"],
                       item_type=row["item_type"], item_id=row["item_id"],
                       amount=row["amount"], currency=row["currency"],
                       status=row["status"], idempotency_key=row["idempotency_key"],
                       created_at=row["created_at"], approved_by=row["approved_by"])
