import json, re, hashlib
from pathlib import Path
root=Path(__file__).parent

# --- Schema Drift Guard ---
# Ensures the served copy (implementation/data/PERSON_SCHEMA_V1.0.json) used by the
# PERSON_SCHEMA_V1.0 runtime validator never silently diverges from the frozen source
# of truth (reference/person-schema/PERSON_SCHEMA_V1.0.json). This guard only compares
# bytes; it never reads or changes the schema's content.
def sha256_of(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
frozen_schema_path=root.parent/'reference'/'person-schema'/'PERSON_SCHEMA_V1.0.json'
served_schema_path=root/'data'/'PERSON_SCHEMA_V1.0.json'
frozen_hash=sha256_of(frozen_schema_path)
served_hash=sha256_of(served_schema_path)
schema_drift_ok=frozen_hash==served_hash
print('SCHEMA DRIFT GUARD:', 'PASS' if schema_drift_ok else 'FAIL')
print('  reference/person-schema/PERSON_SCHEMA_V1.0.json sha256:', frozen_hash)
print('  implementation/data/PERSON_SCHEMA_V1.0.json     sha256:', served_hash)
assert schema_drift_ok, 'Schema drift detected: implementation/data/PERSON_SCHEMA_V1.0.json no longer matches the frozen reference/person-schema/PERSON_SCHEMA_V1.0.json byte-for-byte.'

roster=json.loads((root/'data/core_roster_1000.json').read_text(encoding='utf-8'))
timeline=json.loads((root/'data/timeline_seed_persons.json').read_text(encoding='utf-8'))
candidates=json.loads((root/'data/topic_candidates.json').read_text(encoding='utf-8'))
events=json.loads((root/'data/events.json').read_text(encoding='utf-8'))
actors=json.loads((root/'data/actors.json').read_text(encoding='utf-8'))
assert len(roster)==1000
assert len({x['personId'] for x in roster})==1000
assert all(re.fullmatch(r'p\d{6,}',x['personId']) for x in roster)
assert len({x['identityKey'] for x in timeline})==len(timeline)
assert len({x['candidateId'] for x in candidates})==len(candidates)
assert len({x['eventId'] for x in events})==len(events)
assert len({x['actorId'] for x in actors})==len(actors)
keys={x['identityKey'] for x in timeline}|{x['topicPersonKey'] for x in candidates}
for e in events:
    for k in e.get('personRefs',[]): assert k in keys,(e['eventId'],k)
    for k in e.get('candidatePersonRefs',[]): assert k in keys,(e['eventId'],k)
    for a in e.get('actorRefs',[]): assert any(x['actorId']==a for x in actors),(e['eventId'],a)
for c in candidates:
    if c['candidateId']=='WTP-006':
        assert c['dates']['start'] is None and c['dates']['end'] is None
        assert c['activityRange']=={'start':1422,'end':1429,'precision':'range'}
    if c['candidateId']=='WTP-007':
        assert c['dates']['start'] is None and c['dates']['end'] is None
        assert c['activityRange']=={'start':1669,'end':1672,'precision':'range'}
print('PASS')
print('roster',len(roster))
print('timeline',len(timeline))
print('timeline-ready roster',sum(1 for x in roster if x.get('timelineReady')))
print('topic candidates',len(candidates))
print('events',len(events))
print('actors',len(actors))
print('identity unique',len({x['identityKey'] for x in timeline})==len(timeline))
print('event refs resolved',True)
