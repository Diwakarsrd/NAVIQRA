import { api, configureApi, getApiConfig } from '../src/lib/api';

describe('NAVIQRA API client', () => {
  beforeEach(() => { configureApi('http://localhost:8000'); global.fetch = jest.fn(); });
  afterEach(() => { jest.resetAllMocks(); });
  it('normalizes the base URL and sends trip planning payloads', async () => {
    const plan = { trip_id: 'trip-1', itinerary: { destination: 'Kyoto' }, stages: [], memory_used: [], warnings: [] };
    (global.fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => plan });
    const result = await api.planTrip({ traveler_id: 't1', origin: 'Bengaluru', destination: 'Kyoto', start_date: '2026-12-12', end_date: '2026-12-17', budget: 1200, currency: 'USD', travelers: 2, interests: ['food'], constraints: [] });
    expect(result.trip_id).toBe('trip-1');
    expect(global.fetch).toHaveBeenCalledWith('http://localhost:8000/v1/trips/plan', expect.objectContaining({ method: 'POST' }));
  });
  it('attaches an API key when configured', async () => {
    configureApi('http://localhost:8000/', 'secret');
    (global.fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => ({ status: 'ok' }) });
    await api.health();
    expect((global.fetch as jest.Mock).mock.calls[0][1].headers['X-API-Key']).toBe('secret');
    expect(getApiConfig()).toEqual({ baseUrl: 'http://localhost:8000', hasApiKey: true });
  });
  it('surfaces backend error details', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({ ok: false, status: 401, json: async () => ({ detail: 'Invalid API key' }) });
    await expect(api.health()).rejects.toThrow('Invalid API key');
  });
  it('provides a useful network error', async () => {
    (global.fetch as jest.Mock).mockRejectedValue(new Error('offline'));
    await expect(api.health()).rejects.toThrow('Cannot reach NAVIQRA API');
  });
});
