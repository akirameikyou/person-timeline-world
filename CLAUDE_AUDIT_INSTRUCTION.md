# Claude 現物監査指示｜Person Timeline World v1.0

## 目的
このパッケージは、Person Timeline World v1.0 の現物監査用です。
まず実装を壊さずに読み取り、設計と実装の整合性を確認してください。

## 最初にやること
1. `implementation/` を展開し、README → WORLD_IMPLEMENTATION_SCHEMA_V1.json → PHASE10_WORLD_IMPLEMENTATION_VERIFICATION.md → index.html → app.js → data/* の順に確認。
2. `reference/` は設計・データの基準資料。特に `PERSON_SCHEMA_V1.0.json` は凍結済みなので変更禁止。
3. まず現物監査のみ。勝手にリファクタ、仕様変更、データの書き換え、ID再採番をしない。

## 重点確認
### A. 基本名簿とTopic Required
- Core 1,000人とTopic Required人物が同じ `personId` identity model で再利用できるか。
- Core所属/Topic所属が人物そのもののidentityと分離されているか。
- Topic Requiredは「下位ランク」ではなく「topic-required membership」として扱われているか。
- 同一人物を複数Topicで再利用してもduplicate personが作られないか。

### B. Event ↔ Person
- Event → existing Core person
- Event → verified non-Core / topic-required person
- Event → unverified candidate
- Person → Event
の各リンクが一貫しているか。

### C. Actor typing
- `person / organization / group / social_function_gap` が混同されていないか。
- Eijudōのような組織や匿名職能集団がPersonになっていないか。
- 天明の大飢饉のようなSystemic Eventが、人物の存在を要求せず成立するか。

### D. ID安定性
- Topic Required → Core へ昇格しても `personId` が変わらない構造か。
- Eventリンク、Topicリンク、外部IDが昇格で切れないか。

### E. Data integrity
- 1000人の `personId` 一意性。
- Topic Required候補のID/参照整合性。
- Event/Topic/Actor/Source間の参照切れ。
- Export/Importでリンクとsource lineageが保持されるか。

### F. Time-first interaction
- YEAR FOCUSが人物行クリックに勝手に依存しないか。
- PERSON LIFESPAN BARとheader handleの操作が設計意図どおりか。
- VIEW RANGEとYEAR FOCUSが別操作として保たれているか。

### G. Frozen schema
- `reference/person-schema/PERSON_SCHEMA_V1.0.json` と実装側のpersonデータ構造が矛盾していないか。
- Frozen schemaを変更せず、membership/topic/event linkを別層で表現できているか。

## 追加確認：世界史運用
以下のケースを最低1回、実装上追跡してください。
1. Genghis Khan → Rabban Bar Sauma
2. Zheng He → Ma Huan
3. Kūkai → Huiguo
4. Hokusai → Eijudō / anonymous printers
5. Tenmei famine → group/systemic actors

特に「基本名簿にいない人物をTopic Requiredとして保存し、同じ人物を別Topicで再利用する」ケースを確認してください。

## テスト方法
- 可能ならブラウザを実際に起動し、最小操作テストを実行。
- 不可能なら、JS静的解析・参照整合性・データ構造監査を行い、実行不能の理由を明記。
- Windows環境では `implementation/START_SERVER.bat` を使って確認。

## 出力
最初の回答は次の順で返してください。

1. 現物確認結果
2. PASS / FAIL / WARNING の一覧
3. 実装と設計の不一致
4. 直す必要がある不具合（優先度付き。ただし「政治的な良し悪し」ではなく技術上の重要度）
5. 修正案
6. 追加で必要なデータ
7. 修正前に私へ確認すべき事項

## 重要な制約
- 事実を推測して補完しない。
- 現物にない機能を「ある」と報告しない。
- Core/Topic Requiredにランキングや重要度スコアを導入しない。
- `PERSON_SCHEMA_V1.0.json` を勝手に変更しない。
- まず監査結果を返し、修正は承認後に行う。

## 返却先
清水 晶 / Architect。監査結果をそのまま返してください。
