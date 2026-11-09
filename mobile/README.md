# NAVIQRA Mobile

Premium, mobile-first iOS and Android companion for the NAVIQRA v0.2 FastAPI backend. Built with Expo SDK 54, React Native, TypeScript, Expo Router, TanStack Query, Zustand and AsyncStorage.

## Features

- Discover screen with editorial destination cards and AI concierge entry points.
- AI concierge trip request form wired to `POST /v1/trips/plan`.
- Itinerary detail with day navigation, budget summary, rationale and planning caveats.
- My Trips, Saved Places and Profile screens.
- Persistent local traveler ID, saved destinations and latest itinerary.
- Backend health and capability-compatible API client, traveler memory read/write, provider search and booking preparation/approval methods.
- Optional `X-API-Key` support and editable backend URL for simulators and physical devices.
- Explicit UI copy that demo inventory is not live and a plan is not a booking.

## Requirements

- Node.js 20.19+ recommended
- npm 10+
- Expo Go compatible with SDK 54, or iOS Simulator / Android Emulator
- Python backend from repository root

## Install

```bash
cd mobile
npm install
cp .env.example .env
```

Set `EXPO_PUBLIC_API_URL` in `.env`:

| Runtime | API URL |
|---|---|
| iOS Simulator | `http://127.0.0.1:8000` |
| Android Emulator | `http://10.0.2.2:8000` |
| Physical phone | `http://YOUR_COMPUTER_LAN_IP:8000` |

For a physical phone, both devices must be on the same network and the backend must listen on `0.0.0.0`, for example:

```bash
# From repository root
uvicorn naviqra.api:app --host 0.0.0.0 --port 8000
```

If the backend uses `NAVIQRA_API_KEY`, enter it in Profile → Backend connection. Do not ship a privileged shared API key inside a public mobile binary; production deployments should replace this development mechanism with user-scoped OAuth/OIDC tokens.

## Run

```bash
npm start
npm run android
npm run ios
```

Scan the Expo QR code with Expo Go, or launch on an installed simulator/emulator. The API URL can also be changed inside Profile without rebuilding the app.

## Quality checks

```bash
npm test
npm run typecheck
```

## Backend contract

The app calls the existing v0.2 endpoints:

- `GET /health`
- `GET /v1/platform/capabilities`
- `POST /v1/trips/plan`
- `GET /v1/travelers/{traveler_id}/memories`
- `POST /v1/memories`
- `GET /v1/providers/demo/search?destination=...`
- `POST /v1/bookings/prepare`
- `POST /v1/bookings/{booking_id}/approval`

The current v0.2 planner and provider are deterministic/demo implementations. The mobile client does not claim live inventory, confirmed reservations, payment processing, or LLM-powered chat. Booking endpoints are exposed in the typed API client for the next booking-management screen, while the current app keeps planning separate from purchase.

## Build installable binaries

```bash
npx expo install --check
npx eas-cli build --platform all
```

Configure EAS project ownership, signing credentials, app-store metadata and privacy disclosures before distributing production builds.


## Enterprise v2 integration security

The v2 enterprise SDK is intended for trusted server-to-server integrations. Do not put `X-Tenant-Key`, supplier credentials, or other long-lived secrets in Expo `EXPO_PUBLIC_*` variables or a mobile bundle. A production mobile app must authenticate users through OIDC/OAuth and call a backend-for-frontend that validates user tokens and derives tenant membership server-side. The current mobile release candidate still uses the v1 app API and requires a production authentication integration before store submission.
