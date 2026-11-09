# Provider integration contract

The existing provider protocol is intentionally small. A real supplier adapter must:
- Identify its supplier and supported product types.
- Search using normalized dates, currency, occupancy and destination inputs.
- Return supplier IDs, source timestamps, cancellation rules, taxes/fees and availability expiry.
- Preserve the supplier's terms and attribution.
- Support idempotent booking where the supplier API allows it.
- Distinguish `quoted`, `held`, `confirmed`, `cancelled`, `failed` and `unknown` states.
- Never report a confirmed booking until the supplier confirms it.
- Expose sandbox and live modes separately.

No real supplier credentials are included. Demo provider responses are explicitly non-bookable.
