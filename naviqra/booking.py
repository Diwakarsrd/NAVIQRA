from __future__ import annotations
from naviqra.models import Booking, BookingIntent, BookingStatus
from naviqra.store import SQLiteStore


class BookingService:
    """Approval-gated booking workflow. Demo provider confirms only simulated actions."""
    def __init__(self, store: SQLiteStore) -> None:
        self.store = store

    def prepare(self, intent: BookingIntent) -> Booking:
        existing = self.store.get_booking_by_key(intent.idempotency_key)
        if existing:
            return existing
        booking = Booking(trip_id=intent.trip_id, provider=intent.provider,
                          item_type=intent.item_type, item_id=intent.item_id,
                          amount=intent.amount, currency=intent.currency,
                          idempotency_key=intent.idempotency_key)
        return self.store.create_booking(booking)

    def decide(self, booking_id: str, approved: bool, approver: str) -> Booking:
        booking = self.store.get_booking(booking_id)
        if booking is None:
            raise KeyError("booking not found")
        if booking.status != BookingStatus.PENDING_APPROVAL:
            return booking
        booking.status = BookingStatus.APPROVED if approved else BookingStatus.REJECTED
        booking.approved_by = approver
        return self.store.update_booking(booking)
