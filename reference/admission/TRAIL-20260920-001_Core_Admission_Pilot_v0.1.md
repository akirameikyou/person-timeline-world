# TRAIL-20260920-001｜Person Timeline Core Admission Pilot v0.1

**MODE:** EXPLORE  
**Status:** Pilot design / not an adoption decision  
**Purpose:** Test whether the proposed admission criteria can operate across record-rich, record-poor, mobile, colonial-contact, oral-history, and institutional societies without turning Person Timeline Core into a fixed-number ranking.

---

## 1. Mission

This pilot does **not** decide the final Core, and does **not** rebuild the whole dataset.

It tests whether the following design works in practice:

1. Person-level **Admission** and collection-level **Coverage Audit** are separate.
2. Evidence **form** is separated from evidence **corroboration**.
3. A person's value is described as **Distinct Observation Value**, not "greatness".
4. Regional Floor, Time Slice, Network, and Interface/Counter checks are used as audits, not quotas.
5. The number of Core persons is allowed to emerge from the criteria rather than being fixed in advance.

---

## 2. Model D-Lite to test

### Stage A｜Scope Check

Record whether the candidate can be treated as an individually identifiable historical person and roughly located in time.

Possible date basis:
- life
- reign
- floruit
- activity window

Unknown birth/death dates are allowed.

### Stage B｜Evidence Basis + Corroboration

Record evidence forms independently of confidence.

Candidate vocabulary:
- written_record
- epigraphy
- archaeology
- material_culture
- oral_history
- genealogical_tradition
- indigenous_tradition
- contemporary_external_record
- later_historical_record

Then record **corroboration**, i.e. whether different evidence lineages intersect.

Example:
`[oral_history, archaeology, foreign_contact_log]`

No evidence form is automatically treated as inferior.

### Stage C｜Anchor Candidates

Do not assign rank. Record which functions may be relevant:
- global_anchor
- regional_anchor
- domain_anchor
- network_anchor
- tradition_knowledge_anchor (pilot vocabulary)

### Stage D｜Distinct Observation Value

Question:
> What becomes observable if this person is present that is difficult to observe from existing persons alone?

Pilot vocabulary includes:
- state_formation
- diplomacy
- trade_connection
- religious_transmission
- knowledge_preservation
- scientific_discovery
- artistic_transformation
- navigation
- resistance
- mediation_translation
- social_reproduction
- education
- healing_care
- craft_transmission
- spiritual_ecological_custodianship
- diaspora_connection
- historical_recording

The vocabulary is explicitly provisional.

### Stage E｜Collection Audit

After person-level observations, inspect the collection through four lenses:

1. **Regional Floor** — Can the region be observed through more than rulers and state institutions?
2. **Time Slice** — Do major periods become blank or misleading when YEAR FOCUS moves?
3. **Network Audit** — Are mobile zones such as Silk Road, Indian Ocean, Pacific, diaspora, translation, and religious networks visible?
4. **Interface & Counter Audit** — Are mediators, translators, mixed-position actors, recipients, and counter-positions visible, rather than only rulers vs resisters?

No fixed regional quota is used in the pilot.

---

## 3. Pilot outputs

For each candidate, create an **observation record**, not a score or rank.

Recommended fields:

```json
{
  "person": "...",
  "time_basis": "life | reign | floruit | activity",
  "evidence_forms": [],
  "corroboration": [],
  "anchor_candidates": [],
  "observation_values": [],
  "regions": [],
  "networks": [],
  "interface_or_counter": [],
  "redundancy_question": "",
  "open_verification": [],
  "pilot_note": ""
}
```

The pilot must **not** output a numerical importance score.

---

# 4. Pilot Region A｜1200–1400 Central Asia / Steppe / Silk Road

## Stress test

- Can mobile and transregional persons be represented without forcing them into one modern region?
- Do Persian/Chinese/external written records overwhelm steppe perspectives?
- Can women, administrators, religious envoys, chroniclers, and merchants appear beside khans?
- Can Interface Anchors be captured without making "foreign traveler" equivalent to "regional representative"?

## Candidate pool (20, provisional)

1. Genghis Khan
2. Ögedei Khan
3. Chagatai Khan
4. Batu Khan
5. Möngke Khan
6. Kublai Khan
7. Hulagu Khan
8. Berke Khan
9. Sorghaghtani Beki
10. Töregene Khatun
11. Yelü Chucai
12. Rabban Bar Sauma
13. Rashid al-Din Hamadani
14. Ata-Malik Juvayni
15. Ghazan Khan
16. Öljaitü
17. Özbeg Khan
18. Marco Polo
19. Ibn Battuta
20. Timur

## What this region should test

- ruler density vs distinct observation value
- steppe / sedentary interface
- Buddhist / Christian / Muslim transmission
- chronicler vs participant
- women in dynastic/network transmission
- external observer vs internal historical voice

---

# 5. Pilot Region B｜1600–1750 Japan

## Stress test

This is intentionally a **record-rich region**. The pilot should test whether the model can prune redundancy without using a quota.

Questions:
- Can multiple shoguns be distinguished by observation function rather than office alone?
- Do literature and visual art crowd out mathematics, astronomy, agriculture, education, and women?
- Does abundant documentation create artificial observation value?

## Candidate pool (20, provisional)

1. Tokugawa Ieyasu
2. Tokugawa Hidetada
3. Tokugawa Iemitsu
4. Tokugawa Tsunayoshi
5. Tokugawa Yoshimune
6. Kasuga no Tsubone
7. Hayashi Razan
8. Nakae Tōju
9. Kumazawa Banzan
10. Yamaga Sokō
11. Arai Hakuseki
12. Ogyū Sorai
13. Kaibara Ekken
14. Seki Takakazu
15. Shibukawa Shunkai
16. Miyazaki Yasusada
17. Matsuo Bashō
18. Ihara Saikaku
19. Chikamatsu Monzaemon
20. Kiyohara Yukinobu

## What this region should test

- pruning in a source-rich environment
- office/title duplication
- science and practical knowledge vs literary fame
- women whose surviving records are thinner than male institutional actors
- whether "well documented" is being confused with "necessary observation coordinate"

---

# 6. Pilot Region C｜1400–1800 East & Central Africa / Indian Ocean / Atlantic

## Stress test

- Can external Portuguese/Arabic records and local traditions coexist without one automatically outranking the other?
- Can Kongo, Ethiopia/Horn, Swahili coast, and Madagascar be seen as distinct networks rather than one generic Africa bucket?
- Does the method surface religion, mediation, intellectual history, women, and trade as well as rulers and warfare?

## Candidate pool (20, provisional)

1. Afonso I of Kongo
2. Álvaro II of Kongo
3. Pedro II of Kongo
4. Garcia II of Kongo
5. António I of Kongo
6. Pedro IV of Kongo
7. Njinga of Ndongo and Matamba
8. Kimpa Vita (Dona Beatriz)
9. Ahmad ibn Ibrahim al-Ghazi
10. Gelawdewos
11. Susenyos I
12. Walatta Petros
13. Zera Yacob (the philosopher)
14. Mentewab
15. Mikael Sehul
16. Saif bin Sultan
17. Yusuf bin Hasan of Mombasa — **identity/source verification required before use**
18. Ratsimilaho
19. Andriamasinavalona
20. Andrianampoinimerina

## What this region should test

- evidence-form asymmetry
- external-contact records vs local historical traditions
- women and religious movements
- Atlantic / Indian Ocean interface
- whether modern regional buckets distort historical networks

---

# 7. Pilot Region D｜1800–1950 Pacific / Oceania

## Stress test

- Can indigenous sovereignty, knowledge, language, historical recording, and navigation-related traditions remain visible against the enormous archive of colonial administrations and settler societies?
- Can interface figures be represented without reducing them to "colonial intermediary"?
- Can the system avoid equating document volume with observation value?

## Candidate pool (25, provisional)

1. Kamehameha I
2. Kamehameha III
3. Kalākaua
4. Liliʻuokalani
5. Queen Emma of Hawaiʻi
6. Princess Kaʻiulani
7. David Malo
8. Samuel Kamakau
9. Joseph Nāwahī
10. Hongi Hika
11. Te Whiti-o-Rongomai
12. Tohu Kākahi
13. Tāwhiao
14. Te Kooti
15. Tahupōtiki Wiremu Rātana
16. Apirana Ngata
17. George Tupou I
18. Pōmare IV
19. Cakobau
20. Tupua Tamasese Lealofi III
21. Olaf Frederick Nelson
22. David Unaipon
23. William Barak
24. Truganini
25. Ratu Sir Lala Sukuna

## What this region should test

- settler archive imbalance
- oral / indigenous / written evidence combinations
- sovereignty and cultural transmission
- translators and interface persons
- indigenous intellectuals and historians
- regional diversity inside the large label "Oceania"

---

# 8. Pilot procedure

## Phase 1｜Freeze the criteria for the duration of one region

Do not change the Gate vocabulary halfway through judging one region. Record proposed changes separately.

Purpose: avoid moving the goalposts candidate by candidate.

## Phase 2｜Create evidence cards

For every candidate, record:
- what evidence forms exist
- what must still be verified
- which networks the person touches
- what observation values appear plausible from sources

No admission decision yet.

## Phase 3｜Apply person-level gates

For each person ask only:

1. Can this person be historically located sufficiently for a timeline?
2. Is there a usable evidence basis?
3. Which observation values are directly supportable?
4. Which anchor functions are candidates?
5. Is the apparent value merely duplicated by several nearby people?

Record disagreements rather than forcing consensus.

## Phase 4｜Run the collection audits

For the 15–25 person set, inspect:
- missing time spans
- missing networks
- ruler/politics dominance
- evidence-form dominance
- gender invisibility
- mediator invisibility
- community/knowledge invisibility
- duplicated observation functions

## Phase 5｜Cross-region comparison

Only after all four regions are complete, compare:

- Did Japan produce far more "eligible" observation values simply because evidence is abundant?
- Did Africa/Oceania generate more "unverifiable" notes because evidence forms differ?
- Did mobile Central Asian actors resist regionPrimary?
- Did the model detect mediators and knowledge custodians, or only political actors?

---

# 9. Pilot success / failure indicators

These are **method indicators**, not person scores.

## Signs the criteria are working

- A candidate is not downgraded merely because evidence is oral, archaeological, genealogical, or external.
- Record-rich Japan does not automatically expand without limit.
- Mobile Central Asian figures can be represented without false modern geographic precision.
- East/Central African candidates can be described through more than foreign-contact records.
- Pacific indigenous historians, intellectuals, cultural transmitters, and sovereignty actors remain visible beside colonial documentation.
- Mediators / translators / interface figures can be expressed without forcing them into "ruler" or "resister" categories.
- Explanations remain short enough that two reviewers can understand why a person is being considered.

## Signs the criteria need revision

- "Corroboration" quietly becomes a numeric threshold such as "2 sources = valid" regardless of evidence quality.
- Observation Value becomes an unlimited vocabulary that can justify everyone.
- Regional Floor becomes a hidden quota.
- Time Slice rewards long-lived people merely because they occupy more years.
- Network Anchor becomes a loophole for famous travelers while local people disappear.
- Most disputed cases can only be resolved by subjective "importance" language.

---

# 10. Metrics to record during the pilot

Do not use these to rank persons. Use them to audit the **criteria**.

- unresolved_case_count
- reviewer_disagreement_count
- evidence_form_distribution
- candidates_with_multi-lineage_corroboration
- candidates_relying_on_single_external_record_lineage
- observation_value_frequency
- network_coverage
- duplicate_observation_clusters
- women / mediator / knowledge-custodian visibility as a diagnostic, not a quota
- time-slice gaps

---

# 11. Questions left open by the pilot

1. Should `tradition_knowledge_anchor` remain a separate Anchor, or be absorbed into Domain Anchor?
2. Should Corroboration be recorded only as evidence lineages, or also include a textual assessment of conflicts between lineages?
3. How should a person with only a broad floruit range appear in YEAR FOCUS?
4. How should Core treat a historical person whose surviving identity is strongly shaped by later tradition?
5. Is `regionPrimary` necessary at all for highly mobile actors, or should some persons be network-first?
6. Should "Core" be stored as a property, or generated as a view from qualification + coverage data?
7. What is the simplest Model D-Lite rule set that two independent reviewers can apply with similar results?

---

# 12. Pilot stop condition

The pilot ends after all four regions have been processed once and the criteria have been compared across them.

Do **not** continue adding candidates until each region "feels complete". That would recreate uncontrolled saturation.

At the end, produce:

1. Criteria that worked unchanged
2. Criteria that produced systematic bias
3. Vocabulary that must be revised
4. Cases where reviewers could not reach a clear factual description
5. Proposed Admission Criteria v0.2

No global Core dataset is rebuilt during this pilot.

---

## Next担当／依頼内容／返却先

**Next担当:** GPT + Gemini as separate reviewers during the pilot; Claude only after the data structure needs implementation review.

**依頼内容:** Apply this protocol to the four provisional candidate pools, recording evidence basis, corroboration, observation values, networks, redundancy questions, and open verification issues. Do not produce a ranking and do not finalize the Core.

**返却先:** User for review, then GPT (Architect) for integration into `Person Timeline Core Admission Criteria v0.2`.
