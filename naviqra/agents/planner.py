from __future__ import annotations
from datetime import timedelta
from naviqra.models import Activity, Itinerary, TripRequest


class ItineraryAgent:
    """Rule-based baseline planner. Replace/enrich via pluggable model providers."""
    def plan(self, trip_id: str, request: TripRequest) -> Itinerary:
        days = (request.end_date - request.start_date).days
        daily_budget = request.budget / days
        activities: list[Activity] = []
        for day in range(1, days + 1):
            date_label = (request.start_date + timedelta(days=day - 1)).isoformat()
            activities.append(Activity(
                name=f"Explore {request.destination} — day {day}",
                description=f"Flexible day plan for {date_label}; prioritize {', '.join(request.interests) or 'local highlights'}.",
                day=day, estimated_cost=round(daily_budget * 0.35, 2),
                currency=request.currency, category="discovery",
            ))
        total = round(sum(a.estimated_cost for a in activities), 2)
        return Itinerary(trip_id=trip_id, destination=request.destination,
                         start_date=request.start_date, end_date=request.end_date,
                         activities=activities, estimated_total=total,
                         currency=request.currency,
                         rationale=["Distributed a portion of the stated budget across trip days.",
                                    "Used stated interests as planning signals; verify local hours and availability."])
