# `atcoder` ツールの一般 TODO

ABC 本番対応に限定されない、`atcoder` ツール全般の改善 TODO。ABC 本番対応のロードマップは `abc-todo.md` を参照。

> このファイルは**これからやること**だけを残す。完了した項目はここには残さない:
> 各機能の what / how は要件定義 [`requirements/NNN-*.md`](requirements/)、why (採用理由・却下案・トレードオフ) は決定記録 [`decisions/`](decisions/)、使い方は利用手引 (`docs/tools/atcoder-*-usage.md`) を参照。

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

## AP. DEBUG 行の最小 JSON pretty print (`test/run --pp` / chat `:pp`) 📝 設計済み (未実装)

> 要件詳細は [`requirements/047-debug-json-pretty-print.md`](requirements/047-debug-json-pretty-print.md)。`:debug` ([要件 030](requirements/030-chat-debug-cheat-commands.md)) / watch ペイン波及 ([要件 034](requirements/034-start-debug-watch-sync.md)) / `--json` ([要件 042](requirements/042-test-json-output.md)) で整備した debug パイプラインの**表示層に整形を一段足すだけ**の最小機能。実装は `design` 済みにつき `feature` で着手する。

### 決めたこと (設計)

- `[DEBUG]` 行のうち **ペイロードが単独で valid JSON (`{`/`[` 始まり) のものだけ** を `json.Indent` で 2-space 再インデント。Python `repr`・ラベル付き `key = {...}`・グリッド検出には踏み込まない (言語非依存・`encoding/json` のみ)。
- オプトイン: バッチ `--pp` フラグ / chat `:pp` (`:set pp|nopp`) トグル、既定 off。**verdict・`--json` の `debug` フィールド・exit code・保存値は不変** (整形は表示時のみの純関数 `prettifyDebug`)。
- `--pp` は `-d` と**直交**。`-d` 無しで `--pp` を渡したら stderr に note 1 行 (含意はしない / フットガンだけ消す)。キー順・数値は `json.Indent` で保存 (`Unmarshal`+`Marshal` は使わない)。

### 影響範囲 (設計、未実装)

- 新規 `internal/ui/prettydebug.go` (`prettifyDebug`)、`internal/ui/reporter.go` (`pp bool`)、`cmd/atcoder` の test/run フラグ、`internal/ui/chat_casebuilder.go`/`chat.go` (`:pp`・`header.PP`)、`internal/ui/command_complete.go` (`pp`/`nopp` 補完)、`fixtures/` (JSON debug スモーク)、`docs/tools/atcoder-test-usage.md`。

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
