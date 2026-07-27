# 077: `review missed` の日付範囲指定

## 概要

`atcoder review missed` が前日または `--date` で指定した 1 日だけでなく、`--from` と `--to` で指定する練習日の範囲から未達問題を一覧・復習済みにできるようにする。既存の 1 日指定は互換性のため維持する。

## 背景・目的

復習を数日分まとめて行う場合、日ごとに `review missed --date` を繰り返す必要がある。対象期間を 1 回の一覧で確認し、そこから復習済みを記録できるようにする。

## スコープ

| 区分 | 内容 |
|---|---|
| 当面のスコープ | `--from YYYY-MM-DD --to YYYY-MM-DD` の両端を含む日付範囲から、設定済みの復習条件に合う solve-stat を一覧する |
| 既存互換 | フラグ未指定は前日、`--date` は従来どおり 1 日を対象にする |
| チェック | `--check <id>` は範囲内の一致 1 件だけを更新する。同じ ID が複数日にあり曖昧なら更新しない |
| 対象外 | 相対期間指定、未復習だけへの絞り込み、複数 ID の一括チェック |

## CLI 仕様

```
atcoder review missed [--date YYYY-MM-DD | --from YYYY-MM-DD --to YYYY-MM-DD] [--check <id>]
```

| フラグ | 説明 |
|---|---|
| `--date YYYY-MM-DD` | 従来の 1 日指定。`--from` / `--to` とは併用できない |
| `--from YYYY-MM-DD` | 範囲の開始日。`--to` と必ず対にして指定する |
| `--to YYYY-MM-DD` | 範囲の終了日。開始日・終了日とも範囲に含む |
| `--check <id>` | 範囲内で一意に一致する問題へ `reviewed_at` を記録する |

処理手順:

1. `--date`、`--from`、`--to` をローカル日付として parse し、指定の組合せを検証する。
2. 指定なしなら前日だけ、`--date` ならその日だけ、`--from` / `--to` ならその閉区間を対象にする。
3. `stats.Scan("exercise")` の solve-stat を日付範囲と `review.missed` 条件で絞り、日付順・ID 順に表示する。
4. `--check` 時は範囲内の一致を 1 件だけ許可して `reviewed_at` を部分更新する。

出力例:

```console
$ atcoder review missed --from 2026-07-20 --to 2026-07-22
missed practice — 2026-07-20 through 2026-07-22

  [ ] 2026-07-20  abc357_d  ac=false  editorial=false  exercise/2026/07/20/abc357_d.py
  [ ] 2026-07-22  abc358_e  ac=true   editorial=true   exercise/2026/07/22/abc358_e.py

  2 missed, 0 reviewed
```

1 日指定時の見出し・行形式は従来どおりとする。

## 動作仕様

| 状況 | 動作 |
|---|---|
| `--from` と `--to` の両方 | 閉区間を対象に一覧する |
| `--from` または `--to` の片方だけ | 引数誤り、exit 2 |
| `--date` と範囲フラグの併用 | 引数誤り、exit 2 |
| 開始日が終了日より後 | 引数誤り、exit 2 |
| 不正な日付 | 引数誤り、exit 2 |
| 範囲内で ID が複数一致する `--check` | 曖昧エラー、exit 1。ファイルは更新しない |
| 範囲内で ID が 1 件一致する `--check` | その solve-stat だけを更新する |

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `cmd/atcoder/review.go` | 範囲フラグの parse・検証と range report の結線 |
| `internal/review/missed.go` | 日付閉区間での抽出、範囲を明示する描画を追加。既存の 1 日 API は互換 wrapper とする |
| `internal/review/missed_test.go` | 境界日・並び順・範囲表示・曖昧 ID のテストを追加 |
| `cmd/atcoder/main.go` / `internal/complete/complete.go` | usage と補完候補を更新 |
| `fixtures/run.sh` | 範囲指定と不正な組合せを smoke test に追加 |
| `docs/tools/usage/review.md` | 範囲指定の使い方とエラー規約を追記 |
| `docs/tools/todo.md` | 完了項目として要件へリンクする |

## 非機能要件

- 既存の前日・`--date` の出力と更新挙動を変えない。
- `--check` の曖昧性では解答ファイルを変更しない。
- 日付の比較はローカル日付のみで行い、時刻は比較対象にしない。

## 関連ドキュメント

- [`074-review-missed-practice.md`](074-review-missed-practice.md)
- [`075-review-missed-config.md`](075-review-missed-config.md)
- [`../usage/review.md`](../usage/review.md)
