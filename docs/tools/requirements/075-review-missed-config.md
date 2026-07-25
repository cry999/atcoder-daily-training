# 075: `review missed` の復習対象条件を config で設定する

## 概要

`atcoder review missed` の復習対象条件を、固定の `ac=false OR editorial=true` から config で変更できるようにする。任意の式評価エンジンは入れず、許可した述語だけを `review.missed.conditions` に列挙し、`review.missed.mode` (`any` / `all`) で OR / AND を切り替える。

## 背景・目的

要件 074 では「AC できなかった問題」と「解説を見た問題」を翌日の復習対象にした。運用していくと、たとえば「AC はしたが実装スコアが低い」「目標時間を超えた」「検証スコアが 1 以下」も復習したい日がある。一方で、`record` に `review_required=true` のような専用項目を足すと、既存の AC / editorial / score / duration から導ける情報を二重管理することになる。復習方針は「その問題で起きた事実」ではなく「どう振り返るか」という利用者の好みなので、config に持たせる。

## スコープ

| 区分 | 内容 |
|---|---|
| 当面のスコープ | `review.missed.mode` と `review.missed.conditions` を config に追加し、`review missed` の抽出条件として使う |
| 既定値 | config 未設定なら要件 074 と同じ `any` + `["ac=false", "editorial=true"]` |
| 条件の表現 | 許可した述語文字列のみ。任意の四則演算・括弧・関数呼び出しは持たない |
| config 編集 | `atcoder config set review.missed.mode any` / `atcoder config set review.missed.conditions "ac=false,editorial=true,score.impl<=1"` |
| TOML 手編集 | `conditions = ["ac=false", "editorial=true"]` の配列も許す |
| 対象外 | `record` に復習専用項目を足すこと、`--where` による一時上書き、複雑な式言語 |

## config スキーマ

```toml
[review.missed]
mode = "any" # any | all
conditions = ["ac=false", "editorial=true"]
```

| キー | 型 | 既定 | 説明 |
|---|---|---|---|
| `review.missed.mode` | enum (`any` / `all`) | `any` | 条件を OR (`any`) / AND (`all`) のどちらで評価するか |
| `review.missed.conditions` | string list | `["ac=false", "editorial=true"]` | 復習対象にする条件。`config set` ではカンマ区切り文字列を受け、保存時は TOML 配列にする |

## 条件文法

| 形式 | 例 | 意味 |
|---|---|---|
| `ac=<bool>` / `ac!=<bool>` | `ac=false` | `solve-stat.ac` が一致する |
| `editorial=<bool>` / `editorial!=<bool>` | `editorial=true` | `solve-stat.editorial` が一致する |
| `score.<axis><op><n>` | `score.impl<=1` | 5 軸スコアを比較する |
| `duration<op><duration>` | `duration>=30m` | `duration_ms` を duration 文字列と比較する |
| `duration<op>target` | `duration>target` | `duration_ms` と `target_ms` を比較する |

- `<axis>` は `knowledge` / `translation` / `complexity` / `impl` / `verify`。
- `<op>` は `=`, `!=`, `<`, `<=`, `>`, `>=`。bool は `=` / `!=` のみ。
- 値が未記録の条件は false。例: `score.impl<=1` は `impl` 未記録なら一致しない。`duration>target` は `duration_ms` または `target_ms` が未記録なら一致しない。

## CLI 仕様

既存の `review missed` の構文は変えない。

```console
$ atcoder config set review.missed.conditions "ac=false,editorial=true,score.impl<=1"
set review.missed.conditions = ac=false,editorial=true,score.impl<=1  (...)

$ atcoder review missed
missed practice — 2026-07-24
...
```

処理ステップ:

1. `cmdReviewMissed` が `config.Load()` で config を読む。
2. `review.missed.mode` / `conditions` を `internal/reviewrule` で parse / validate する。
3. `internal/review.BuildMissed` に rule を渡し、対象日かつ `HasStat` の solve だけを評価する。
4. 条件未設定なら既定 rule (`any`, `ac=false`, `editorial=true`) を使い、要件 074 の挙動を保つ。

## 動作仕様

| 状況 | 動作 |
|---|---|
| config 無し | 既定条件で動く |
| `conditions` が空 | 既定条件で動く (`[]` は「未設定」と同じ扱い) |
| `mode=any` | 条件のいずれかに一致すれば復習対象 |
| `mode=all` | 条件すべてに一致したら復習対象 |
| 条件文法が不正 | `config set` では exit 2、手編集 config を読んだ `review missed` でも exit 2 |
| 未記録フィールド | 条件は false |

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/reviewrule/` | 条件 parser / evaluator を追加 |
| `internal/config/` | `Review.Missed` スキーマ、typed keys、補完候補、validation を追加 |
| `internal/review/missed.go` | 固定 `isMissed` を rule 評価に差し替える |
| `cmd/atcoder/review.go` | config 読み込み・条件 parse エラーを exit 2 で返す |
| `fixtures/run.sh` | config 条件によって復習対象が変わる smoke を追加 |
| docs | config / review の利用手引とテスト戦略を更新 |

## エラーハンドリング

| 状況 | 動作 | exit |
|---|---|---|
| config.toml 文法エラー | 既存 config parse error | 2 |
| `review.missed.mode` が `any` / `all` 以外 | invalid config value | 2 |
| 未知条件 (`difficulty>=800` 等) | invalid config value | 2 |
| bool に比較演算 (`ac<=true`) | invalid config value | 2 |
| score 軸や値が不正 | invalid config value | 2 |
| duration 値が不正 | invalid config value | 2 |

## 非機能要件

- 既存挙動を壊さない: config 未設定では要件 074 と同じ。
- 任意式を評価しない: 文字列 DSL は固定述語だけに閉じ、実装・エラー表示・前方互換を軽く保つ。
- `review missed --check` の書き込み対象は、config 条件で抽出された一覧に限定する。
- `record` は事実を記録する層のまま保ち、復習方針は config に寄せる。

## 関連ドキュメント

- 復習キュー: [`074-review-missed-practice.md`](074-review-missed-practice.md)
- solve-stat: [`061-solve-record-stats.md`](061-solve-record-stats.md)
- config 基盤: [`007-atcoder-config.md`](007-atcoder-config.md) / [`009-atcoder-config-subcommand.md`](009-atcoder-config-subcommand.md)
- 利用手引: [`../usage/review.md`](../usage/review.md) / [`../usage/config.md`](../usage/config.md)
