# TRAIL-20260924 — World Implementation Verification

## Status
IMPLEMENTATION PILOT — PASS WITH CONTROL NOTE

## Verification targets

1. Base roster and collection membership are separated.
2. Event candidate can be saved as Topic Required without entering the base roster.
3. Topic Required has a stable local key and separate Event link records.
4. Duplicate person creation is blocked by candidate identity / normalized name lookup.
5. One Topic Required person can be linked from more than one Event.
6. Export/import uses a dedicated Topic Layer envelope.
7. Person, organization, group, institutional group, and social-function gap remain distinct.
8. Timeline interaction preserves the v0.3.1 rule: lifespan bar/header handle changes YEAR FOCUS; empty timeline/ruler changes VIEW RANGE.

## Dataset checks

- base roster: 1,000
- timeline seed: 162
- exact roster↔timeline enriched matches: 37
- event seeds: 8
- actor registry records: 6
- topic candidates: 7
- frozen PERSON_SCHEMA_V1.0 changed: NO

## Important data control

No guessed identity mapping was added. Only exact English-name matches between the provisional 1,000 roster and the enriched prototype were treated as direct mappings. Other prototype records retain their separate seed identity.

Shakushain and Shō Hashi are not given life dates from event dates. Where life dates are unresolved, the candidate remains unplaced on the life timeline and retains an activity-range field in the candidate data.

## Manual test sequence

EVENTS → Kūkai event → Save + Link Huiguo → TOPIC REQUIRED → confirm one record and one event link → link same person to another event → confirm one person / multiple links → Export → Reset Local → Import → confirm restoration.

Browser automation could not be run in this container because the managed Chromium profile blocks local/file URLs with `ERR_BLOCKED_BY_ADMINISTRATOR`. JavaScript syntax, JSON structure, identity uniqueness, and event-reference integrity were verified in the working container.
