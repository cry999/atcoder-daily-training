# `atcoder update` / `atcoder version` 自己更新 要件定義

## 概要

`atcoder` 自身を **1 コマンドで最新版に入れ替える** `atcoder update` と、**現在の版・最新版が出ているかを確認する** `atcoder version` / `atcoder update --check` を追加する。このツールのソースはこの GitHub リポジトリ自身なので、最新版の取得・インストールは Go ツールチェインに委譲し (`go install github.com/cry999/atcoder-daily-training/cmd/atcoder@latest`)、バージョンの識別は Go が自動で実行ファイルに埋め込む VCS 情報 (`runtime/debug.ReadBuildInfo`) を使う。**git タグ運用は行わない** (リリース作業ゼロ)。

読み取り専用ではない唯一の例外 (= 自分自身のバイナリを置き換える) だが、解答ファイル・キャッシュ・設定には一切触れない。

## 背景・目的

- ツールはこのリポジトリの `cmd/atcoder` を `go install ./cmd/atcoder` して `PATH` 上の `atcoder` として使っている。機能追加が進む中、**手元の `atcoder` が古いまま** になりやすく、「今入っているのはいつのコミットか」「最新が出ているか」を確かめる手段が無い。
- 毎回 `cd` してリポジトリに戻り `git pull && go install ./cmd/atcoder` を打つのは摩擦。**どの cwd からでも `atcoder update` の 1 コマンド** で最新に揃えたい。
- バージョン管理のためにタグを打つ・`-ldflags` で版番号を注入する、といったリリース作業はこの個人ツールには重い。Go は VCS リポジトリからビルドした実行ファイルに **コミット sha・コミット日時・dirty フラグを自動で埋め込む** (`go build`/`go install` の buildvcs)。これを「現在版」とすれば、タグ無しでも版を識別できる。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 更新元 | GitHub (Go module proxy) の最新。`go install <module>/cmd/atcoder@latest` | GitHub Releases のプリビルドバイナリ、リポジトリ内からの再ビルド |
| 版の持ち方 | Go の自動 VCS スタンプ (commit sha / commit time / dirty) | semver git タグ + `-ldflags -X` |
| 最新判定 | module proxy の `@latest` (pseudo-version の日時・sha) と埋め込み版を比較 | リリースチャンネル、changelog 表示 |
| コマンド | `atcoder version` / `atcoder update` / `atcoder update --check` | `--force` 再インストール、`update --to <version>` |
| インストール先 | `go install` の規定 (`$GOBIN` または `$GOPATH/bin`)。ツール側では制御しない | 任意の出力先指定 |
| 副作用 | 自分自身のバイナリ置き換えのみ。解答・キャッシュ・設定には触れない | — |

### 境界 (他機能との分担)

- `status` / `login` (要件 009) の AtCoder 認証・ネットワークとは無関係。`update` が触る外部は **Go module proxy / GitHub と go ツールチェインだけ**で、AtCoder には一切アクセスしない。
- `config` (要件 007) とも独立。更新先や proxy はツール設定に持たず、go の環境変数 (`GOPROXY`/`GOBIN` 等) にそのまま委ねる。

## 前提・依存

- **`go` コマンドが `PATH` 上にあること。** 更新は go ツールチェインに委譲する (このツールは自前でビルド/ダウンロードしない)。`go` が無ければエラー (exit 1)。
- **ネットワーク必須** (`update` と `--check`)。proxy/GitHub に到達できなければエラー (exit 1)。`atcoder version` は**オフラインで動く** (埋め込み情報を読むだけ)。
- モジュールが解決できること (公開リポジトリ前提)。`GOBIN`/`GOFLAGS` 等のユーザ環境は尊重する。

> **実装時の修正 (バグ対応)**: 当初は `GOPROXY` もそのまま尊重する設計だったが、proxy.golang.org が `@latest` をキャッシュするため push 直後に古いコミットを最新として返し、「最新のはずが古い版がインストールされる」不具合が出た。対策として **このツール自身のモジュールだけを `GOPRIVATE` に入れ、proxy を介さず git remote へ直接解決する**ように変更 (依存モジュールは通常どおり proxy 経由)。また `go install …@latest` 由来のバイナリは VCS スタンプが付かないため、現在版は **モジュールの pseudo-version からも読む**ようにした。詳細は `docs/tools/usage/update.md` の「バージョン表示について」。

## バージョンの持ち方 (自動 VCS スタンプ)

`runtime/debug.ReadBuildInfo()` から以下を読む:

| 取得元 | 内容 | 例 |
|---|---|---|
| `bi.Main.Path` | このツールのモジュールパス | `github.com/cry999/atcoder-daily-training` |
| `bi.Main.Version` | モジュール版。`@latest` 由来なら pseudo-version、ローカルビルドは `(devel)` | `v0.0.0-20260609...-def5678` / `(devel)` |
| setting `vcs.revision` | ビルド元コミット sha (フル) | `def5678abc...` |
| setting `vcs.time` | コミット日時 (RFC3339) | `2026-06-09T12:34:56Z` |
| setting `vcs.modified` | 作業ツリーが dirty だったか | `true` / `false` |

- モジュールパスは `bi.Main.Path` を優先し、取れなければ定数 `github.com/cry999/atcoder-daily-training` にフォールバック (リネーム耐性)。
- `go run` や `-buildvcs=false` でビルドされた等で VCS 設定が無い場合は **"unknown" 扱い** (version はそれでも exit 0、update は最新版だけ示して継続)。

## CLI 仕様

```
atcoder version
atcoder update [--check]
```

| コマンド / フラグ | 説明 |
|---|---|
| `atcoder version` | 現在インストールされている版 (commit sha 短縮・コミット日時・dirty) を表示。オフライン・副作用なし |
| `atcoder update` | 最新版を確認し、現在版と違えば `go install …@latest` で入れ替える |
| `atcoder update --check` | 確認だけ行い、**インストールはしない**。現在版・最新版・更新の要否を表示 |

### 処理ステップ

**`atcoder version`**

1. `ReadBuildInfo()` を読む。
2. `<short-rev> (<commit-date>)[ dirty]` 形式で 1〜数行表示。VCS 情報が無ければ `unknown` と表示。
3. exit 0。

**`atcoder update [--check]`**

1. 現在版 (埋め込み VCS) を読む。
2. 最新版を解決する: 中立 dir (一時 dir) を cwd にして `go list -m -json <module>@latest` を実行し、JSON の `Version` (pseudo-version) と `Time` を得る。※ 中立 dir にするのは、このツール自身のリポジトリ内で実行されても module 文脈に引きずられないため。
3. 更新要否を判定する (下記「最新判定ロジック」)。
4. `--check` のとき: 現在版・最新版・要否を表示して終了 (インストールしない)。check が成功すれば **要否によらず exit 0**、解決に失敗したら exit 1。
5. `--check` でないとき:
   - 既に最新なら "already up to date" を表示して exit 0 (再インストールしない)。
   - 更新があれば `go install <module>/cmd/atcoder@latest` を実行 (中立 dir を cwd、環境は継承して `GOBIN`/`GOPROXY` 等を尊重、go の stdout/stderr をそのまま流す)。成功で installed 版を表示し exit 0、失敗で exit 1。

### 最新判定ロジック

- 現在版が `unknown` → 「比較不能。最新は <latest>」と表示し、更新ありとして扱う (入れ替えを許可)。
- `vcs.modified == true` (dirty ビルド) → 「ローカル改変ビルドのため正確に比較できない」と警告しつつ、最新版を表示。`update` は実行を続ける。
- それ以外: 最新 pseudo-version 末尾の sha が現在 `vcs.revision` の短縮と一致、または最新 `Time` ≤ 現在 `vcs.time` なら **最新**。最新 `Time` が新しく sha も異なれば **更新あり**。

### 出力イメージ

```
$ atcoder version
atcoder def5678 (2026-06-09T12:34:56Z)

$ atcoder update --check
  current  abc1234 (2026-06-05T09:00:00Z)
  latest   def5678 (2026-06-09T12:34:56Z)
  update available — run `atcoder update`

$ atcoder update
  current  abc1234 (2026-06-05T09:00:00Z)
  latest   def5678 (2026-06-09T12:34:56Z)
  installing… go install github.com/cry999/atcoder-daily-training/cmd/atcoder@latest
  installed def5678 ✓

$ atcoder update            # 既に最新
  already up to date (def5678, 2026-06-09T12:34:56Z)
```

## 動作仕様

| 状況 | 挙動 |
|---|---|
| `version` (VCS 情報あり) | 短縮 sha + コミット日時 (+ dirty) を表示、exit 0 |
| `version` (VCS 情報なし) | `unknown` 表示、exit 0 |
| `update --check` で更新あり | 現在/最新/「update available」を表示、exit 0 (インストールしない) |
| `update --check` で最新 | 現在/最新/「up to date」を表示、exit 0 |
| `update` で更新あり | `go install …@latest` 実行、成功で exit 0 |
| `update` で既に最新 | "already up to date" を表示、再インストールせず exit 0 |
| `update` 中の dirty ビルド | 警告して最新版を表示しつつ入れ替えは実行 |
| 最新版の解決失敗 (proxy/network/go なし) | エラー表示、exit 1 |
| `go install` 失敗 | go の stderr を見せて exit 1 |
| 未知フラグ | usage 表示、exit 2 |

- **cwd 非依存**: `go list`/`go install` は中立 dir を cwd に設定して実行するため、どこから呼んでも同じ結果。リポジトリ内/外を問わない。
- **入れ替え以外に副作用なし**: 解答・キャッシュ・`config.toml`・git に触れない。インストール先は go ツールチェイン任せ (`$GOBIN`/`$GOPATH/bin`、既に `PATH` 上にある前提)。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| 新規 `cmd/atcoder/version.go` | `cmdVersion(args []string) (int, error)`。ビルド情報を整形表示 |
| 新規 `cmd/atcoder/update.go` | `cmdUpdate(args []string) (int, error)`。`--check` フラグ解析、現在/最新の表示、`go install` 実行 |
| `cmd/atcoder/main.go` | dispatch に `case "version"` / `case "update"` を追加。`usage()` に 2 行追記 |
| 新規 `internal/selfupdate/` | バージョン取得・最新解決・インストールのドメインロジック (cmd から分離してテスト可能に) |
| `internal/complete/complete.go` | サブコマンド候補に `version` / `update` を追加 (説明付き、要件 012)。`update` のフラグ表に `--check`。`valueFlags` 変更なし (--check は値を取らない) |
| `internal/complete/complete_test.go` | `version`/`update` がサブコマンド候補に出る期待を追加 |
| `fixtures/run.sh` | `version` の exit 0 (オフライン) を smoke。`update` の引数誤り (exit 2) を smoke。ネットワーク経路 (`update`/`--check`) はオフライン化の工夫が要る (下記テスト方針) |
| `docs/tools/usage/update.md` | 利用手引 (新規。version/update/--check のインストール手順と前提) |
| `docs/tools/todo.md` | 項目 L として記載し、本要件へ相互リンク |

### 新規 `internal/selfupdate/` パッケージの責務 (素描)

```go
package selfupdate

// Current はビルド時に埋め込まれた VCS 情報から現在版を読む。
// VCS 情報が無ければ Known=false。
type Current struct {
    Module   string // モジュールパス (bi.Main.Path)
    Revision string // vcs.revision (フル sha)。Known=false なら空
    Time     time.Time
    Modified bool // dirty ビルドか
    Known    bool
}

func ReadCurrent() Current

// Latest は go module proxy から最新 pseudo-version を解決する。
// 中立 dir を cwd に `go list -m -json <module>@latest` を実行して JSON を読む。
type Latest struct {
    Version string // pseudo-version (例 v0.0.0-2026...-def5678)
    Sha     string // pseudo-version 末尾の短縮 sha
    Time    time.Time
}

func ResolveLatest(ctx context.Context, module string) (Latest, error)

// Available は cur と latest から更新の要否を返す (unknown/dirty の扱いを含む)。
func Available(cur Current, latest Latest) bool

// Install は `go install <module>/cmd/atcoder@latest` を中立 dir で実行し、
// 出力を w にストリームする。go 不在・install 失敗は error。
func Install(ctx context.Context, module string, w io.Writer) error
```

- 外部コマンド (`go`) 実行と `runtime/debug` 読み取りはこのパッケージに閉じ込め、cmd 層は表示と exit code 分類だけにする。
- モジュールパス・`/cmd/atcoder` サブパスは定数に持ちつつ、実行時は `ReadCurrent().Module` を優先する。

## エラーハンドリング

| 状況 | 動作 | exit |
|---|---|---|
| 未知フラグ (`update --bogus` 等) | usage 表示 | 2 |
| `version` (VCS 情報の有無を問わず正常) | 表示 | 0 |
| `update --check` の check 成功 (更新あり/最新を問わず) | 表示 | 0 |
| 最新版の解決失敗 (network/proxy/`go` 不在) | エラー表示 | 1 |
| `go install` 失敗 | go の stderr を提示 | 1 |
| `update` 成功 (入れ替え or 既に最新) | 表示 | 0 |

- exit code 規約を踏襲: 引数/フラグ誤り = 2、実行時失敗 (解決・install 失敗) = 1、成功 = 0。
- **`--check` の exit code は「更新あり」を区別しない** (成功なら 0)。スクリプトから「更新あり」を終了コードで判定したい場合は将来拡張 (専用コード) とする。可否は stdout のテキストで伝える。

## 非機能要件

- **既存非破壊**: 既存サブコマンドの挙動・usage・exit code は不変。dispatch に case を 2 つ足すだけ。`go.mod` の依存は増やさない (標準ライブラリ + `os/exec` で `go` を呼ぶのみ)。
- **依存ゼロ追加 / FW 非導入**: 標準 `flag` のまま。バージョン埋め込みは Go の buildvcs に任せ、`-ldflags` も追加しない。
- **cwd 非依存・冪等**: どこから呼んでも同じ。既に最新なら何もしない。同じ最新版を二度 `update` しても結果は同じ。
- **オフライン耐性 (version)**: `atcoder version` はネットワーク不要。`update`/`--check` だけがネットワークを要する。
- **安全**: 触るのは自分自身のバイナリのみ。解答・キャッシュ・設定・git に副作用を持たない。AtCoder へはアクセスしない。

## テスト方針 (feature への申し送り)

- **オフラインで固定できる経路**:
  - `atcoder version` → exit 0 (ビルド情報の有無で文言は変わるが必ず 0)。
  - `atcoder update --bogus` → exit 2 (フラグ誤り)。
  - `internal/selfupdate` の `Available()` と pseudo-version パースはユニットテストで網羅 (現在=unknown/dirty/同一/古い/新しい、最新 sha 抽出)。
- **ネットワーク経路の smoke**: `fixtures/run.sh` は AtCoder にも GitHub にも触らない方針。`update`/`--check` の成否を run.sh で直接叩くのは避け、代わりに:
  - `GOPROXY=off` を与えて `update --check` が **決定的に exit 1 (解決失敗)** になる経路を smoke する、もしくは
  - file ベースの proxy (`GOPROXY=file://…` に最小モジュールを置く) を用意して `--check` の成功経路を固定する。
  - どちらを採るかは実装時 (feature) に決める。少なくとも version (exit 0) と update 引数誤り (exit 2) は run.sh に載せる。

## 将来の拡張ポイント

- `atcoder update --force`: 最新と同じでも再インストール (壊れたバイナリの修復)。
- `atcoder update --to <version>`: 特定版へピン留め。
- semver git タグ運用へ移行し、`version` を `v1.2.3` 表示に (リリース作業とのトレードオフ)。
- `--check` の終了コードで「更新あり」をシグナルする (スクリプト連携)。
- GitHub Releases のプリビルドバイナリ取得 (go ツールチェイン非依存のインストール経路)。
- changelog / 直近コミット一覧の表示。

## 用語

- **VCS スタンプ**: Go が `go build`/`go install` 時に実行ファイルへ自動で埋め込むリポジトリ情報 (`vcs.revision`/`vcs.time`/`vcs.modified`)。`runtime/debug.ReadBuildInfo()` で読む。
- **pseudo-version**: タグの無いモジュールに対し go module proxy が返す版文字列 (`v0.0.0-<日時>-<短縮sha>`)。`@latest` はタグがあればタグ、無ければ既定ブランチ最新コミットの pseudo-version を指す。
- **中立 dir**: `go list`/`go install` を実行するときに cwd に据える、どのモジュールにも属さない一時ディレクトリ。リポジトリ内実行時の module 文脈干渉を避けるため。
- `contest_id`/`contest_num`/`task_id`/`letter` は既存要件に準拠 (本機能では使わない)。

## 関連ドキュメント

- `docs/tools/requirements/006-rename-cli-to-atcoder.md` (CLI 名 `atcoder` 化・`go install ./cmd/atcoder` の前提)
- `docs/tools/requirements/008-atcoder-completion.md` / `012-completion-descriptions.md` (サブコマンド/フラグ補完にここで `version`/`update` を足す)
- `docs/tools/requirements/059-update-local-check.md` (`update --check` をローカル作業ツリー比較に拡張する子要件)
- `docs/tools/usage/update.md` (利用手引。本機能で新設)
- `docs/tools/todo.md` (上位ロードマップ。項目 L として記載)
