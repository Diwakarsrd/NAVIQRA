export type Activity = { name: string; description: string; day: number; estimated_cost: number; currency: string; category: string };
export type Itinerary = { trip_id: string; destination: string; start_date: string; end_date: string; activities: Activity[]; estimated_total: number; currency: string; rationale: string[]; created_at?: string };
export type AgentPlan = { trip_id: string; stages: string[]; itinerary: Itinerary; memory_used: MemoryRecord[]; warnings: string[] };
export type MemoryRecord = { id: string; traveler_id: string; kind: string; key: string; value: unknown; created_at: string };
export type ProviderResult = { id: string; type: 'stay' | 'activity' | 'flight' | string; name: string; price: number; currency: string; source: string; bookable: boolean };
export type Booking = { id: string; trip_id: string; provider: string; item_type: string; item_id: string; amount: number; currency: string; status: string; idempotency_key: string };
export type TripInput = { traveler_id: string; origin: string; destination: string; start_date: string; end_date: string; budget: number; currency: string; travelers: number; interests: string[]; constraints: string[] };
