# `atcoder` ツールの一般 TODO

ABC 本番対応に限定されない、`atcoder` ツール全般の改善 TODO。ABC 本番対応のロードマップは `abc-todo.md` を参照。

> このファイルは**これからやること**だけを残す。完了した項目はここには残さない:
> 各機能の what / how は要件定義 [`requirements/NNN-*.md`](requirements/)、why (採用理由・却下案・トレードオフ) は決定記録 [`decisions/`](decisions/)、使い方は利用手引 (`docs/tools/usage/*.md`) を参照。

## AV. 実装記録・正答率・5 軸スコア (`atcoder record`) ✅ DONE (MVP, 8e6dc32)

> 要件詳細は [`requirements/061-solve-record-stats.md`](requirements/061-solve-record-stats.md)。利用手引は [`usage/record.md`](usage/record.md)。集計母体・Now 注入の流儀は [J / 要件 005](requirements/005-exercise-stats.md)、stats read-only の決定は [ADR 0002](decisions/0002-stats-readonly-exercise-tree.md)、実提出/AC 取得が不可な理由は [ADR 0006](decisions/0006-fold-submit-into-test.md)。

### 解きたい問題

- 現状の `stats` は「解答ファイルが存在するか」だけを数え、**どれだけ時間をかけたか・自力で AC できたか・どこでつまずいたか**が残らない。振り返りが「解いた/解いてない」の粒度に留まる。
- 練習の質を上げるには「どの局面 (知識・読解・計算量見積もり・実装・検証) が弱いか」を軸ごとに点数化して積み上げたい。実装時間も体感でなく実測で残したい。

### 決まったこと (MVP で実装したこと)

- 1 問の記録を **実装時間・AC (bool)・解説閲覧 (bool)・5 軸スコア (各 0–3)** として、解答ファイル冒頭の **solve-stat コメントブロック** (`# >>> atcoder-stat >>>` … `# <<< atcoder-stat <<<`) に埋める。Python コメントなので実行・判定・提出に影響しない。書き込みはキー単位の部分更新 + temp/rename の atomic、破損ブロックは自動修復せず停止。
- ライフサイクル: `atcoder start` / `record start` が `started_at` を刻む → `test --submit` 後の AC プロンプト or `record stop` で `solved_at`/`duration_ms` 確定 → `record` で AC/解説/5 軸を記録。AC は自己申告 (実提出/オンライン判定は Turnstile のため不可、[ADR 0006](decisions/0006-fold-submit-into-test.md) のまま)。
- 難易度 (= **category × letter**) ごとの**目標実装時間**を `config set target.<category>.<letter> <dur>` で設定。`record`/`record stop` が記録時点の目標を `target_ms` にスナップショットし、目標比・達成率を出す。
- `atcoder stats` に solve-stat があると `recorded` (ac率・自力AC率・editorial率・median time・target達成率) と `score (avg)` の 2 セクションが増える。記録が無ければ従来出力のまま (後方互換)。母集団 N と記録済み M の差を明示。
- 不変則: 解答ファイル不可侵 (書くのは記録系コマンドのみ、stats は read-only) / exit code (引数誤り=2・実行時失敗=1・成功=0) / 標準 `flag` 維持 / 前方互換 (未知キーは読み飛ばし)。

### 影響範囲 (実装済み)

- 新規 `internal/solvestat/` (`Stat`/`Score`・`Parse`/`Merge`/`Overwrite`・`ReadFile`/`Update`/`OverwriteFile`)、新規 `cmd/atcoder/record.go` (`record`/`record start`/`record stop` dispatch + 対話/非対話)、`cmd/atcoder/start.go` (着手刻印 + `--restart`)、`cmd/atcoder/submitprep.go` (提出後 AC プロンプト)、`cmd/atcoder/main.go` (dispatch/usage/builtins)。`internal/config/` (`[target.<category>]` 2 階層動的マップ + `TargetDuration`)、`internal/stats/{stats,render}.go` (solve-stat 読み込み経路 + `Record` 集計 + `recorded`/`score` セクション)、`internal/cliargs` (`--score`/`--time`/軸フラグを値フラグに)、`internal/complete` (`record` 候補・フラグ)。テスト: `internal/solvestat/solvestat_test.go`・`internal/config/target_test.go`・`internal/stats/record_test.go`・`fixtures/run.sh` (record スモーク群)。docs: `usage/record.md` (新規)・`usage/stats.md`・`usage/start.md`・`fixtures/README.md`・`atcoder-test-testing.md`・`CLAUDE.md`。
- Phase 2 (別出荷): `atcoder record edit` (専用編集 UI)・chat TUI (Ctrl+S) 経路の AC プロンプト・`review` への per-cell 表示。MVP でも `record` 再実行でキー単位訂正は可能。

## H. エディタ・テンプレート連携

### 解きたい問題

- 練習でも本番でも、新規問題ファイルを開いた直後はいつも同じ boilerplate (`import sys; input=sys.stdin.readline`、`from collections import defaultdict` 等) を書くことになり、書き始めまでの摩擦が大きい。
- 練習用の `atcoder new` は当日 dir を mkdir するだけで、ファイルは生成していない。

### 決めること

- テンプレートの所在
  - 候補 1: リポジトリ内 `templates/python.py` (git で履歴管理、共有しやすい)
  - 候補 2: `$XDG_CONFIG_HOME/atcoder-daily-training/templates/python.py` (個人設定として分離)
  - 第一候補は **リポジトリ内**。1 人のリポジトリなので個人設定と区別する利得は薄い。
- テンプレート選択方法
  - 候補: `atcoder new --task d --template default` のように名前指定。デフォルトは "default"。
  - 言語ごとに複数テンプレート (`python_basic.py`, `python_io_fast.py` 等) を持てるようにする。
- 既存ファイルとの衝突
  - 既にファイルがある場合は上書きしない (確認プロンプトもしくは `--force` で上書き)。
- どのコマンドから生成されるか
  - `atcoder new --task d`: 当日 dir に `<task>.py` を生成 (現状は dir のみ作成)
  - ABC 本番対応 (`abc-todo.md` の B) の `contest prepare` でも内部的にこのテンプレート生成を呼ぶ
- テンプレート内の変数展開 (`{{task}}`, `{{contest}}`, `{{date}}` 等を埋め込むか、純粋なテキストか)
- テンプレートの形式 (Go の `text/template` 等を使うか、単純文字列か)

### 影響範囲

- 新規 `templates/` ディレクトリ
- 新規 `internal/template/` パッケージ
- `cmd/atcoder/new.go` の拡張
- ABC ロードマップの B (contest prepare) と接続

### 関連項目

- `abc-todo.md` の B (コンテストメタの取り扱い): contest prepare の中で全タスクのスケルトンを一括生成する。テンプレート機構をそこから呼べるようにしておく。

## AP. DEBUG 行の最小 JSON pretty print (`test/run --pp` / chat `:pp`) ✅ DONE (dee5a9d)

> 要件詳細は [`requirements/047-debug-json-pretty-print.md`](requirements/047-debug-json-pretty-print.md)。`:debug` ([要件 030](requirements/030-chat-debug-cheat-commands.md)) / watch ペイン波及 ([要件 034](requirements/034-start-debug-watch-sync.md)) / `--json` ([要件 042](requirements/042-test-json-output.md)) で整備した debug パイプラインの**表示層に整形を一段足すだけ**の最小機能。利用手引は [`usage/test.md`](usage/test.md) の「JSON デバッグ出力の整形」節。

### 決まったこと (実装したこと)

- `[DEBUG]` 行のうち **ペイロードが単独で valid JSON (`{`/`[` 始まり) のものだけ** を `json.Indent` で 2-space 再インデント。Python `repr`・ラベル付き `key = {...}`・グリッド検出には踏み込まない (言語非依存・`encoding/json` のみ)。
- オプトイン: バッチ `--pp` フラグ / chat `:pp` (`:set pp|nopp`) トグル、既定 off。**verdict・`--json` の `debug` フィールド・exit code・保存値は不変** (整形は表示時のみの純関数 `prettifyDebug`)。
- `--pp` は `-d` と**直交**。`-d` 無しで `--pp` を渡したら stderr に `note: --pp has no effect without -d/--debug` を 1 行 (含意はしない / フットガンだけ消す)。キー順・数値は `json.Indent` で保存 (`Unmarshal`+`Marshal` は使わない)。

### 影響範囲 (実装済み)

- 新規 `internal/ui/prettydebug.go` (`prettifyDebug`/`prettifyJSONPayload`)・`internal/ui/prettydebug_test.go`、`internal/ui/reporter.go` (`TestReporter`/`RunReporter` に `pp bool` + コンストラクタ引数)、`cmd/atcoder/{test,adhoc}.go` (`--pp` フラグ + `-d` 無し note + 伝播)、`internal/runexec/runexec.go` (`Options.PP`/`ChatHeader.PP`)、`internal/ui/chat.go` (`ChatHeader.PP` + ingestion で整形 + `renderMsgBlock` の複数行対応)、`internal/ui/chat_casebuilder.go` (`:pp`・`:set pp|nopp`・`setPP`/`togglePP`・cheat)、`internal/ui/command_complete.go` (`pp`/`nopp` 補完)、`internal/complete/complete.go` (`--pp` shell 補完)。fixture: `fixtures/fixture_debugjson.py` + cache + `run.sh` (`-d --pp` 整形/非整形/note スモーク)。docs: `usage/test.md`・`fixtures/README.md`・`atcoder-test-testing.md`。

## AV. `atcoder update` の go ツールチェイン非依存な更新経路 (優先度: 低)

> 実装済みの自己更新 ([要件 050](requirements/050-atcoder-self-update.md)、`--check` のローカル比較は [要件 059](requirements/059-update-local-check.md)) の将来拡張ポイント。要件 050 の「将来の拡張ポイント」にも記載。

- 現状の `update` は `go install …@latest` に委譲するため、利用環境に `go` が必要。`go` 無しでも更新できるよう、GitHub Releases のプリビルドバイナリを取得して自身を差し替える経路を将来用意する (OS/arch 判定・ダウンロード・実行ファイルの atomic 置換・チェックサム検証が要る)。
- リリースを発行する運用が前提になるので、当面は優先度低め。

## AW. 機械可読出力の段階 1 の残り + nvim 薄フロント (段階 2)

> `test --json` ([要件 042](requirements/042-test-json-output.md)) で始めた「コアは Go CLI エンジン / UI は薄グルー」方針の続き。全面書き直しも全面 TUI 重装化もせず、bubbletea 版 TUI は並走で残す。

### 段階 1 の残り (機械可読出力)

- `stats --json` / `review --json`: それぞれの nvim 機能を作る段で `test --json` と同じ流儀で機械出力を足す。
- `--watch --json` (NDJSON): 再判定のたびに 1 行 JSON を流し nvim 側がライブ更新。

### 段階 2 (nvim 薄フロント)

- nvim Lua フロントの増設 (薄グルー)。`vim.system()` でコア CLI を叩き quickfix / diff 表示。competitest.nvim のテストケースの扱い方 (Competitive Companion 受信 port 27121・diff トグル・popup/split UI・テンプレ) を参考にする。

## K. 提出ジャッジ状況の確認 (`atcoder status` / `login`) ❌ 撤去 (実現不可・再着手しないこと)

### 経緯と撤回理由 (再着手しないこと)

一度 `atcoder login` / `logout` / `status`（認証付きで `/submissions/me` を取得し verdict 表示）を実装したが、**実現不可と判明し全削除した**。理由:

- **AtCoder のログインページは Cloudflare Turnstile (ボット対策) で保護されている。** ブラウザが JS で生成する検証トークン (`cf-turnstile-response`) が無いと、正しい username/password でも認証が拒否される（→ 汎用エラー `Error.`）。`online-judge-tools` 等の既存ツールも同条件では programmatic ログイン不可。
- 回避策としてブラウザの `REVEL_SESSION` cookie を取り込む方式（`--session-cookie` 等）も実装したが、毎回 DevTools から cookie を手でコピーする運用が重く、利用者判断で**機能ごと不要**となった。
- **認証なし経路も不可:** AtCoder の提出一覧はログイン必須で列挙できず、kenkoooo AtCoder Problems API は反映まで約 5 分の遅延・コンテスト中の提出を含まない・第三者依存。即時性が要る用途に合わない。

要件・利用手引・実装（`cmd/atcoder/{login,status}.go`、`internal/atcoder/`、`config.SessionPath`、補完・fixture）は削除済み。再挑戦する場合は **Turnstile を解けるブラウザ自動化**が前提になる点に注意。

> **類似ツール横断調査 (2026-06-16)**: oj / atcoder-cli (acc) / AtCoder Tools いずれも正攻法ログインは Turnstile で全滅し、**生存策はブラウザの `REVEL_SESSION` cookie 取り込みのみ**に収束。submit POST 自体は有効 cookie があれば通る。詳細・出典は [`docs/knowledge/atcoder-auth-state.md`](../knowledge/atcoder-auth-state.md)。本撤去判断は業界現状と一致し、再導入するなら cookie 取り込み方式 (UX が重い) 一択。
