# `atcoder` ツールの一般 TODO

ABC 本番対応に限定されない、`atcoder` ツール全般の改善 TODO。ABC 本番対応のロードマップは `abc-todo.md` を参照。

> このファイルは**これからやること**だけを残す。完了した項目は決定記録 (ADR) に移している:
> 採用理由・却下案・トレードオフは [`docs/tools/decisions/`](decisions/) を、機能の使い方は `docs/tools/atcoder-*-usage.md` を、仕様は `docs/tools/requirements/NNN-*.md` を参照。
>
> 完了済み (ADR 化済み): I. `test --watch` ([ADR 0001](decisions/0001-test-watch-mtime-polling.md)) / J. `stats` ([ADR 0002](decisions/0002-stats-readonly-exercise-tree.md)) / ユーザ設定ファイル ([ADR 0003](decisions/0003-user-config-xdg-toml.md)) / `completion` ([ADR 0004](decisions/0004-shell-completion-no-framework.md))。
>
> 完了済み (要件のみ): `stats --graph` 草表示 (contribution graph)。レベルはローカルのレター重み (`a`=1…`g`=7) で算出し、オフライン・読み取り専用を維持 ([要件 011](requirements/011-stats-graph.md))。

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

## L. ツール自己更新 (`atcoder update` / `version`) 📝 設計済み

### 解きたい問題

- ツールはこのリポジトリの `cmd/atcoder` を `go install` した `atcoder` として使うが、機能追加が進む中で**手元のバイナリが古いまま**になりやすい。「今入っているのはいつのコミットか」「最新が出ているか」を確かめる手段が無く、毎回 `cd` してリポジトリで `git pull && go install ./cmd/atcoder` するのは摩擦。

### 決まったこと

> 要件詳細は [`docs/tools/requirements/013-atcoder-self-update.md`](requirements/013-atcoder-self-update.md)。設計のみ (未実装)。

- `atcoder version` で現在版 (Go 自動埋め込みの commit sha・日時・dirty) を**オフライン表示**。`atcoder update` で最新版に入れ替え、`atcoder update --check` は確認のみ (インストールしない)。
- **更新元は GitHub (module proxy)**。`go install <module>/cmd/atcoder@latest` を Go ツールチェインに委譲し、どの cwd からでも動く。`go list -m -json <module>@latest` で最新を解決。
- **版の持ち方は Go の自動 VCS スタンプ** (`runtime/debug.ReadBuildInfo`)。git タグ運用・`-ldflags` は行わない (リリース作業ゼロ)。
- 触るのは**自分自身のバイナリのみ**。解答・キャッシュ・設定・git・AtCoder には一切触れない。`go` 必須・`version` 以外はネットワーク必須。
- exit code 規約踏襲 (引数誤り=2 / 解決・install 失敗=1 / 成功=0)。`--check` は成功なら更新有無に関わらず 0。

### 影響範囲

- 新規 `cmd/atcoder/{version,update}.go`, `internal/selfupdate/` (バージョン取得・最新解決・install)
- `cmd/atcoder/main.go` (dispatch + usage)、`internal/complete/` (`version`/`update`/`--check` 補完)
- `fixtures/run.sh` (version=exit 0・update 引数誤り=exit 2。ネットワーク経路は GOPROXY オフ等で固定)
- `docs/tools/atcoder-update-usage.md` (利用手引・新規)

### 関連項目

- 補完への登録は要件 008 / 012。CLI 名 `atcoder` 化と `go install ./cmd/atcoder` 前提は要件 006。

## K. 提出ジャッジ状況の確認 (`atcoder status` / `login`) ✅ DONE

### 解きたい問題

- `atcoder submit` は提出ページをブラウザで開くだけで、提出後の verdict (`WJ` → `AC`/`WA`/`TLE`/`RE`/`CE`) はブラウザに切り替えて自分で確認している。「今出したファイルの今のジャッジ結果」をターミナルから確認できると往復が消える。

### 決まったこと

> 要件詳細は `docs/tools/requirements/009-atcoder-status.md`、利用手引は `docs/tools/atcoder-status-usage.md`。

- 着手前調査の結論どおり**認証あり経路を採用**（認証なしは AtCoder の提出一覧がログイン必須・kenkoooo は約 5 分遅延で即時性が出ないため）。
- `atcoder login` (username/password → `REVEL_SESSION` cookie を `session.json` 0600 に保存、**パスワードは保存しない**) → `atcoder status <contest> [--task <task>] [--watch]` で認証付き `/submissions/me` を取得し最新提出の verdict を表示。`atcoder logout` で cookie 削除。
- **即時・コンテスト中も・AtCoder 公式データ**で取れる。kenkoooo (約 5 分遅延) の no-auth fallback は `internal/atcoder.Source` 抽象の別実装として将来追加できる seam を残した (未実装)。
- 取得元 `Source` 抽象 / cookie 任意の HTTP client / `/submissions/me` パーサ / verdict 確定判定 `IsFinal` を分離。パーサ・ログイン・session は単体テスト + ネットワーク非依存 smoke 済み。実 HTML・実ログインの最終確認はユーザのアカウントが要る。
- exit code 規約: 取得成功=0 (AC/WA いずれでも)、未ログイン/失効/未検出/取得失敗=1、引数誤り・非 TTY login=2。`--watch` は下限 2s・Ctrl+C=0。

### 将来の拡張

- no-auth fallback (kenkoooo, 約 5 分遅延・終了後のみ) を未ログイン時の `Source` 実装として追加。
- `atcoder submit` 後に自動で `status --watch` を起動する導線。複数アカウント・keyring 連携。
