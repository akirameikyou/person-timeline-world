# World Implementation v1.0 — AI Team Handoff

## Core behavior to preserve

- Person identity is separate from collection membership.
- Event-derived named people can become Topic Required without becoming Core.
- Topic Required records persist locally and link to Events.
- The same person can be reused across Topics without duplication.
- Organizations, groups, and social-function gaps stay outside the Person layer.
- `PERSON_SCHEMA_V1.0` remains unchanged.

## Next production work

1. Verify and normalize the 1,000 roster metadata.
2. Map the enriched timeline seed to canonical Person IDs only with explicit identity evidence.
3. Verify Event source lineages.
4. Decide final Actor Registry schema.
5. Keep Core promotion as a collection-audit decision, not an automatic consequence of being Topic Required.
