# Person Timeline World v1.0 — Implementation

### 中心構造

```text
BASE ROSTER
   ↓
EVENT / TOPIC
   ↓
TOPIC REQUIRED PERSON
   ↓
local save + link
```

Topic Requiredは基本名簿の「下位人物」ではなく、現在観察しているTopic/Eventを成立させるために必要になった人物です。

## 実装済み

- 1,000人の暫定基本名簿をROSTERに読み込み
- 日付付きtimeline seedをTIME FIRSTタイムラインへ表示
- CORE / TIMELINE SEED / TOPIC REQUIREDを分離
- YEAR FOCUSとVIEW RANGEを分離
- 人物バー / ヘッダー▼ドラッグ
- Event→Topic Required保存
- 同名・既存人物の重複抑止
- Topic RequiredのIndexedDB保存
- Event ↔ Person link
- 同一Topic Required人物の複数Event利用
- Export / Import Topic Layer
- Organization / Group / Social Function GapをPerson化しない
- 天明の大飢饉をSystemic Process Stress Caseとして保持

## データ状態

`core_roster_1000.json` はv0.2機械移入名簿で、全メタデータは未監査です。
`timeline_seed_persons.json` はv0.3.1 UIストレステスト由来の暫定データです。
`events.json` は実装検証用のEvent Seedであり、最終Event Schemaではありません。

`PERSON_SCHEMA_V1.0`は変更していません。

## 起動

Windows 11では `START_SERVER.bat` を実行するか、フォルダ内で:

```text
python -m http.server 8000
```

その後 `http://localhost:8000/` を開きます。
