# NAVIQRA v0.5.0 — 4-minute technical demo

**Opening (20 sec):** “NAVIQRA is not a booking marketplace or a travel chatbot. It is an open infrastructure layer for travel agents to coordinate context and workflows across providers. The marketplace or supplier remains authoritative for inventory, pricing, payments, and booking.”

**1. Capability discovery (30 sec):** Open `/docs`, show `/v2/tenants/{tenant_id}/capabilities` and `/providers`. Explain tenant credentials and the synthetic-only provider.

**2. Provider boundary (45 sec):** POST `/v2/tenants/demo/providers/sandbox/search` with `{"destination":"Lisbon","category":"accommodation"}`. Point out `bookable:false`, `inventory_mode:synthetic_non_bookable`. This proves the adapter contract, not live supply access.

**3. Portable memory (45 sec):** Write profile and procedural memory, then retrieve them. Explain five memory tiers and tenant scoping. Show deletion endpoint and audit trail.

**4. Group consensus (35 sec):** Cast weighted votes for two stays and retrieve ranked candidates. Explain transparent weighted scoring, not opaque preference inference.

**5. Recovery (45 sec):** Run the recovery agent with two synthetic alternatives. Highlight `requires_human_confirmation:true`; NAVIQRA does not autonomously purchase or rebook.

**6. Audit and close (40 sec):** Open `/audit`, show provider search and deletion events. Close: “The next step is a buyer-defined sandbox integration against an authoritative supplier API, with security and operational requirements agreed first.”

**Do not demo:** fake live flight prices, supplier credentials, or a purchase flow that is not connected to a verified provider.
