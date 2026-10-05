# PHASE11 — World Roster Integration v0.1

## Status
INTEGRATION PILOT — PASS WITH KNOWN DATA-COVERAGE GAPS

## Basis
WORLD PERSON TIMELINE v1.0 — ARCHITECTURE FROZEN (Person Identity / Collection Membership / Event / Topic / Actor Registry / Systemic Event / Time First / PERSON_SCHEMA_V1.0 / Schema Drift Guard).

**Architecture was not changed in this pass.** No file under `reference/` was touched. `app.js`, `index.html`, `styles.css`, `config.json`'s structural keys, and `PERSON_SCHEMA_V1.0.json` (both copies) are byte-identical to the frozen state confirmed at end of the prior session. Only two new report artifacts (`WORLD_ROSTER_INTEGRATION_V0.1.json`, `WORLD_ROSTER_LINK_AUDIT.json`) and this document were added.

## What "Integration" means here
This pass connects the existing 1,000-entry roster, 162-person timeline seed, 8 events, 7 topic candidates, 6 actors, and 8 topics as one live, running system in a real browser (IndexedDB-backed), and verifies that Cases A–E resolve correctly end to end — not as isolated unit checks, but as one operating dataset a curator could actually use.

## Case walkthrough (real data, verified live)

| Case | Chain | Result |
|---|---|---|
| A | Genghis Khan (`roster:p000124`) → EVT-001 → Rabban Bar Sauma (`candidate:WTP-003`) | Resolved. Core person and topic candidate both reachable from the event; not yet saved to Topic Required in this pass (candidate remains `topic_candidate`, untouched — no action was needed to demonstrate resolution). |
| B | Zheng He (`roster:p000072`) → EVT-002 → Ma Huan (`candidate:WTP-002`) | Resolved, same basis as A. |
| C | Kūkai (`roster:p000104`) → EVT-003 → Huiguo (`candidate:PCH-001`) | **Saved for real via Save + Link.** `topic:PCH-001` created, `personId=p900001` assigned at Core Candidate stage, Schema Validation run honestly → **FAIL** (record lacks `historicity`/`classification`/`geography`/`anchorTypes`/`externalIds`/`sources`/`admissionStatus`/`dataQualityStatus`/`auditStatus`, and `dates` is shaped as `{start,end,precision}` rather than the schema's `{datingBasis,birth,death}`). No fields were fabricated to force a pass. Curator Approval correctly blocked while validation is FAIL. |
| D | Hokusai (`roster:p000134`) → EVT-004 → Nishimuraya/Eijudō (`ORG-001`, organization) → anonymous woodcutters/printers (`GAP-001`, social_function_gap) | Resolved. Neither actor was converted to a person; `candidatePersonRefs` is empty on this event. |
| E | Tenmei famine (EVT-005) → rural (`GRP-001`), fishing (`GRP-002`), food-management authorities (`GRP-003`, institutional_group), urban distribution (`GRP-004`) | Resolved. `personRefs`/`candidatePersonRefs` both empty; event is fully valid without a named person. The 1783 Asama link exists only in the event's note/placeRefs text in this dataset, not as a separately linked event — flagged as a known gap, not fabricated this pass. |

Full machine-readable detail: [`WORLD_ROSTER_INTEGRATION_V0.1.json`](WORLD_ROSTER_INTEGRATION_V0.1.json).

## The reuse loop (Section 12 of the brief)

`ROSTER → EVENT → NEW ACTOR → TOPIC REQUIRED → save → reuse from a second EVENT`

- **Mechanism: verified, live.** Huiguo was saved for real from EVT-003. Re-invoking the reuse path under a second, clearly-labeled mechanism-check event (not real history, excluded from the JSON deliverables) added only a second link — no duplicate person. The Possible-Match dialog (same name, different candidate ID) correctly forced an explicit A/B/C human choice rather than auto-merging; all three paths (link-to-existing, save-as-separate, hold-for-review) were exercised and behaved correctly.
- **Real-data gap, honestly reported:** the current 8-event seed dataset has no *second real event* that independently needs the same Topic Required person — each of the 7 candidates is referenced by exactly one event today. This is a data-coverage gap, not a mechanism defect, and closing it with genuine, sourced history is out of scope for v0.1 (no large-scale event authoring was requested or performed).

## PASS / WARNING / FAIL / UNIMPLEMENTED

### PASS
1. Roster 1000/1000 displayed
2. Timeline renders (162 timeline-seed rows)
3. Events view renders (8 cards)
4. Core Person → Event (Genghis Khan → EVT-001)
5. Event → Core Person (EVT-001 → Genghis Khan resolves in roster)
6. Event → Topic Required (Huiguo saved from EVT-003)
7. Topic Required persisted to IndexedDB
8. Same-candidate reuse is idempotent (no duplicate person/link on re-invocation)
9. Possible Match dialog (same name, different candidate ID) — A/B/C all verified live, no silent auto-merge
10. Topic Required → Core Candidate (personId `p900001` assigned, membership stays `topic_required`)
11. Schema Validation runs and reports honestly (Huiguo: FAIL, 17 concrete reasons; mechanism-check record: PASS)
12. Curator Approval correctly blocked while validation is FAIL
13. Core Member reachable *only* when validation=PASS and approval=APPROVED (verified via mechanism-check record; personId `p999999` invariant across all 4 stage transitions)
14. personId invariant across every observed stage transition (Huiguo: `p900001` through core_candidate → canonical_person_pending; mechanism record: `p999999` through all 4 stages)
15. Event link (`linkId`) unchanged across every stage transition
16. Reload persistence (membership, stage, personId, validation status, approval status all survive reload)
17. Export/Import round-trip (0 records after clear → full restoration after import)
18. Tenmei systemic event: zero person/candidate refs, 4 group-level actors, valid event
19. Hokusai/Eijudō actor separation: organization and social_function_gap correctly kept out of the Person layer
20. YEAR FOCUS / VIEW RANGE remain independently controllable (drag mechanics unchanged from prior session; re-confirmed at the state level this pass)
- Roster personId uniqueness (1000/1000), timeline identityKey uniqueness (162/162), candidateId/eventId/actorId uniqueness, and all event→person/candidate/actor references resolve (0 unresolved) — see `WORLD_ROSTER_LINK_AUDIT.json`
- Schema Drift Guard: `reference/person-schema/PERSON_SCHEMA_V1.0.json` and `implementation/data/PERSON_SCHEMA_V1.0.json` are byte-identical (SHA-256 `2BDCC889...403DAE` both sides)

### WARNING
- No event in the current 8-event seed dataset naturally reuses a Topic Required person across two *real* events (see reuse-loop section above). Recommend authoring one properly sourced event in a future phase to close this with genuine history.
- 4 sources in `sources.json` (Hokusai/Tenmei-related) remain unreferenced by any candidate/event — not broken, just unused; likely reserved for future candidate authoring.
- `addManualTopic` (manual, non-event-triggered Topic Required entry) still uses a blocking alert rather than the A/B/C dialog on name collision. Unchanged this pass; flagged as a known asymmetry, not fixed here (would have been a scope-exceeding change).

### FAIL
- None found this pass.

### UNIMPLEMENTED
- Authoring of a second real, sourced event that reuses an existing Topic Required person (explicitly out of scope for v0.1 per "no large-scale data addition").
- Modeling the 1783 Asama eruption as its own linked event rather than prose inside EVT-005.
- A/B/C possible-match flow for the manual (non-event) Topic Required entry path.

## Architecture Freeze status

**Maintained.** Every check in this pass exercised the frozen v1.0 architecture as-is: Person Identity (personId stability across all pipeline stages), Collection Membership (roster_entries vs topic_required vs core, never conflated), Event/Topic/Actor Registry structure, Systemic Event modeling (Tenmei), Time First interaction (YEAR FOCUS/VIEW RANGE separation), PERSON_SCHEMA_V1.0 (validated against, never altered, never met by fabrication), and the Schema Drift Guard (confirmed in sync). No architecture file, schema file, or the 1,000-entry roster was modified. The only additions are this report and the two audit JSON files, which are read-only artifacts — they are not wired into `app.js` and do not change runtime behavior.

## Deliverables
- `PHASE11_WORLD_ROSTER_INTEGRATION_REPORT.md` (this file)
- [`WORLD_ROSTER_INTEGRATION_V0.1.json`](WORLD_ROSTER_INTEGRATION_V0.1.json) — Case A–E detail, event/person/actor matrix, reuse-loop status, known gaps
- [`WORLD_ROSTER_LINK_AUDIT.json`](WORLD_ROSTER_LINK_AUDIT.json) — identity uniqueness, reference integrity, orphan sources, actor typing audit, duplicate-detection test, Schema Drift Guard result, personId/link stability audit
