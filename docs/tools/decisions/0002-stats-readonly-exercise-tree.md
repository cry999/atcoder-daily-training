# ADR 0002: `stats` は `exercise/` ツリーのみを読み取り専用で集計する

- ステータス: Accepted
- 日付: 2026-06-09
- 実装: `dd3c3a8` (`feat(stats): add daily practice statistics`)
- 関連: [requirements/005-exercise-stats.md](../requirements/005-exercise-stats.md) / [atcoder-stats-usage.md](../atcoder-stats-usage.md)

## コンテキスト

毎日 `exercise/YYYY/MM/DD/` に解答を積み上げているが、「どれくらい続けられているか」「どの種類に偏っているか」「最近の推移」を振り返る手段が無く、`find | wc -l` を都度叩くしかなかった。モチベーション維持にはストリーク (連続練習日数) と推移の可視化が効く。

## 決定

`atcoder stats [--week | --month | --year]` を追加し、練習の積み上がりをテーブル表示する。

- **集計対象は `exercise/YYYY/MM/DD/*.py` のみ**。1 ファイル = 1 問、日付はパス由来。`abc/`・`adt/` 等の他ツリー横断はしない (ツリーごとに日付の持ち方が違い、横断は別設計が要る)。
- 統計項目は解答数・アクティブ日数・current/longest ストリーク・カテゴリ別 (コンテスト種別 / レター)・時系列 (週/月は日別、年/全期間は週別)。
- 期間指定は相対のみ (`--week`/`--month`/`--year`、デフォルト全期間)。任意日付範囲 (`--since`/`--until`) は将来拡張。
- **読み取り専用・オフライン**。ネットワーク・認証・キャッシュ・解答ファイルに一切触れない。
- 集計ロジックは純粋関数 (`internal/stats.Compute`) に切り出し、`Now` を注入してユニットテストする。

## 結果

- `cmd/atcoder/stats.go` と `internal/stats/` (集計 + レンダリング + テスト) が増えた。
- 純粋関数 + `Now` 注入で、相対期間の集計を決定的にテストできる。
- `exercise/` 限定なので、本番 (`abc/`) や ADT の練習量は数えない。日付がパスに無いツリーを含めるには将来の拡張が要る (既知の割り切り)。

## 却下した代替案

- **全ツリー横断集計**: `abc/<contest>/<letter>.py` 等は日付情報を持たず、mtime や git log に頼ると集計がぶれる。パスに日付が明示される `exercise/` に限定する方が信頼でき、まずそこから。
- **mtime / git ベースの日付**: ファイルを後から触ると集計が動く。パス由来の日付に固定して安定させた。
