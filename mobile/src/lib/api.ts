import type { AgentPlan, Booking, MemoryRecord, ProviderResult, TripInput } from '../types/api';

const DEFAULT_URL = process.env.EXPO_PUBLIC_API_URL || 'http://127.0.0.1:8000';
let configuredUrl = DEFAULT_URL.replace(/\/$/, '');
let configuredKey = '';

export function configureApi(baseUrl: string, apiKey = '') {
  configuredUrl = baseUrl.trim().replace(/\/$/, '');
  configuredKey = apiKey.trim();
}
export function getApiConfig() { return { baseUrl: configuredUrl, hasApiKey: Boolean(configuredKey) }; }

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json', ...(init.headers as Record<string, string> || {}) };
  if (configuredKey) headers['X-API-Key'] = configuredKey;
  let response: Response;
  try {
    response = await fetch(`${configuredUrl}${path}`, { ...init, headers });
  } catch {
    throw new Error(`Cannot reach NAVIQRA API at ${configuredUrl}. Check that the backend is running and the device can reach this address.`);
  }
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const detail = typeof body.detail === 'string' ? body.detail : `Request failed (${response.status})`;
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string; version: string; database: string; authentication: string }>('/health'),
  capabilities: () => request<{ name: string; version: string; capabilities: string[]; providers: { name: string; mode: string; live_inventory: boolean; booking_enabled: boolean }[]; execution_policy: { purchase_requires_approval: boolean; demo_provider_is_non_bookable: boolean } }>('/v1/platform/capabilities'),
  planTrip: (payload: TripInput) => request<AgentPlan>('/v1/trips/plan', { method: 'POST', body: JSON.stringify(payload) }),
  search: (destination: string) => request<{ results: ProviderResult[]; notice: string }>(`/v1/providers/demo/search?destination=${encodeURIComponent(destination)}`),
  memories: (travelerId: string) => request<MemoryRecord[]>(`/v1/travelers/${encodeURIComponent(travelerId)}/memories`),
  saveMemory: (travelerId: string, key: string, value: unknown) => request<MemoryRecord>('/v1/memories', { method: 'POST', body: JSON.stringify({ traveler_id: travelerId, key, value }) }),
  prepareBooking: (payload: { trip_id: string; provider: string; item_type: 'stay' | 'flight' | 'activity'; item_id: string; amount: number; currency: string; idempotency_key: string }) => request<Booking>('/v1/bookings/prepare', { method: 'POST', body: JSON.stringify(payload) }),
  decideBooking: (id: string, approved: boolean, approver: string) => request<Booking>(`/v1/bookings/${encodeURIComponent(id)}/approval`, { method: 'POST', body: JSON.stringify({ approved, approver }) }),
};
