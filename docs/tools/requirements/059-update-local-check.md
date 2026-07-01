# `atcoder update --check` ローカル最新確認 要件定義

## 概要

`atcoder update --check` に、リモート (`@latest`) だけでなく **ローカル作業ツリー (git HEAD) との比較** を加える。これまで `--check` は「インストール済みバイナリ」と「リモートの最新コミット」しか比べておらず、**手元のソースを基準にした最新かどうか** が分からなかった。本要件は **確認 (`--check`) の表示を拡張するだけ** で、`update` / `update --local` の入れ替え挙動そのものは変えない。

要件 050 (`atcoder update` / `atcoder version`) の拡張。インストール・副作用は一切増やさない (git は読み取りのみ)。

## 背景・目的

- インストール済みバイナリが **作業ツリーから dirty でビルドされている** (`go install ./cmd/atcoder` した直後など) と、`vcs.modified == true` のため従来の `--check` は機械的に「update available」と表示してしまう。実際にはインストール版の方が **リモート `@latest` (push 済み HEAD) より新しい** ことが多く、ここで素直に `atcoder update` するとダウングレードになる。表示が実態とずれる。
- ローカルで機能追加を進めているとき、知りたいのは 2 つの問い:
  - **リモート基準**: GitHub に push された最新に対して、入っているバイナリは古いか。
  - **ローカル基準**: いま手元にチェックアウトしている作業ツリー (未 push・未コミット含む) に対して、入っているバイナリは古いか (= `atcoder update --local` で入れ直すと変わるか)。
- 現状の `--check` は前者しか答えられない。後者を同じ 1 コマンドで併せて確認できるようにする。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| ローカル基準点 | cwd の git 作業ツリーの **HEAD コミット (sha・日時) と dirty 状態** | ブランチ名・upstream との ahead/behind |
| 比較対象 | インストール済みバイナリ (`vcs` / pseudo-version) vs ローカル HEAD | 任意の 2 版指定 |
| 対象コマンド | `atcoder update --check` の **表示のみ** | `atcoder version` への併記、`update` 実行時の併記 |
| dirty 判定 | tracked ファイルの未コミット変更 (`git status --porcelain --untracked-files=no`) | Go ファイル限定の差分検出 |
| 入れ替え挙動 | **変更しない** (`update` / `--local` のインストール条件・出力はそのまま) | local 基準での自動入れ替え |

### 境界 (他機能との分担)

- リモート解決 (`@latest` / GOPRIVATE 直接解決) は要件 050 のまま。本要件は git をローカルで読むだけで、proxy/network 経路は触らない。
- **git ahead/behind (ローカル ⇄ origin) は対象外**。本要件のローカル比較は「インストール済みバイナリ ⇄ 作業ツリー HEAD」だけ。リポジトリ同期状況は `git status` の領分とする。
- AtCoder には一切アクセスしない (要件 050 と同じ)。

## ローカル状態の読み方

cwd で `git` を読み取り専用で呼ぶ (書き込みなし):

| 取得 | コマンド | 内容 |
|---|---|---|
| HEAD sha | `git rev-parse HEAD` | 作業ツリーの現在コミット (フル sha) |
| HEAD 日時 | `git show -s --format=%cI HEAD` | コミット日時 (RFC3339) |
| dirty | `git status --porcelain --untracked-files=no` | 出力が非空なら tracked に未コミット変更あり |

- cwd がリポジトリ外 / `git` 不在 / 取得失敗 → **`Known=false`** (エラーにしない)。`--check` は local 行を「n/a」と表示してリモート確認は続行する。
- `--untracked-files=no` にするのは、`exercise/` 等の **未追跡の練習解答が dirty 扱いされる誤検出を避ける** ため (それらは Go バイナリのビルドに無関係)。

## CLI 仕様

コマンド・フラグ表は要件 050 のまま (新フラグなし)。変わるのは `--check` の **出力だけ**。

### 処理ステップ (`atcoder update --check`)

1. インストール済み版 (埋め込み VCS / pseudo-version) を読む。
2. **ローカル作業ツリー版を読む** (上表。失敗時 `Known=false`)。
3. リモート最新を解決する (要件 050 と同じ。GOPRIVATE 直接解決)。
4. `installed` / `local` / `remote` の 3 基準点を表示する。
5. **2 つの判定**を表示する:
   - `remote:` — installed と remote の関係 (下記「リモート判定」)。
   - `local:` — installed と作業ツリー HEAD の関係 (下記「ローカル判定」)。
6. リモート解決に成功すれば exit 0、失敗したら **local 行と local 判定までは表示してから exit 1** (リモート確認は要件 050 どおり実行時失敗扱い)。

### リモート判定 (installed ⇄ remote)

| 状態 | 条件 | 表示 |
|---|---|---|
| up to date | remote sha == installed sha | `remote: up to date` |
| installed newer | installed のコミット日時が remote より新しい | `remote: up to date (installed is newer than origin)` |
| update available | remote のコミット日時が installed より新しい | `remote: update available — run \`atcoder update\`` |
| indeterminate | installed が unknown | `remote: cannot compare (installed version unknown)` |

- dirty ビルドでも **コミット日時で比較**するため、「installed の方が新しい」を正しく言える (従来の「常に update available」を解消)。`update` (入れ替え) 側の判定 (`Available`) は従来のまま変更しない。

### ローカル判定 (installed ⇄ 作業ツリー HEAD)

| 状態 | 条件 (上から順に評価) | 表示 |
|---|---|---|
| n/a | 作業ツリーを読めない (`Known=false`) | `local: n/a — run inside the repo to compare with local source` |
| dirty | 作業ツリーに未コミット変更あり | `local: rebuild available — run \`atcoder update --local\` (working tree has uncommitted changes)` |
| unknown installed | installed が unknown | `local: rebuild available — run \`atcoder update --local\` (installed version unknown)` |
| modified build | installed が dirty ビルド (`vcs.modified`) | `local: rebuild available — run \`atcoder update --local\` (installed binary was built from a modified tree)` |
| ahead | installed sha != 作業ツリー HEAD sha | `local: rebuild available — run \`atcoder update --local\` (local source is ahead of the installed binary)` |
| matches | 上以外 (clean・同一 sha) | `local: up to date (installed matches local source)` |

### 出力イメージ

```
$ atcoder update --check          # 手元で dirty ビルドを入れている / 未 push が手元に進んでいる
  installed  69d5e73 (2026-06-25T21:59:30Z) dirty
  local      69d5e73 (2026-06-25T21:59:30Z) dirty
  remote     ca3f863 (2026-06-25T21:06:48Z)

  remote: up to date (installed is newer than origin)
  local:  rebuild available — run `atcoder update --local` (working tree has uncommitted changes)

$ atcoder update --check          # クリーンで最新が入っている
  installed  ca3f863 (2026-06-25T21:06:48Z)
  local      ca3f863 (2026-06-25T21:06:48Z)
  remote     ca3f863 (2026-06-25T21:06:48Z)

  remote: up to date
  local:  up to date (installed matches local source)

$ atcoder update --check          # リポジトリ外で実行
  installed  ca3f863 (2026-06-25T21:06:48Z)
  local      n/a (not in a repo working tree)
  remote     def5678 (2026-06-27T08:00:00Z)

  remote: update available — run `atcoder update`
  local:  n/a — run inside the repo to compare with local source
```

## 動作仕様

| 状況 | 挙動 |
|---|---|
| `--check`・リポジトリ内・リモート解決成功 | installed/local/remote の 3 行 + remote/local 判定、exit 0 |
| `--check`・リポジトリ外 | local 行は n/a、remote 判定は通常どおり、exit 0 |
| `--check`・リモート解決失敗 | installed/local 行 + local 判定までは表示、リモートエラーを stderr に出し exit 1 |
| `update` (入れ替え) / `update --local` | **従来どおり** (本要件で変更しない) |
| `atcoder version` | **従来どおり** (オフライン・git 非依存。本要件で変更しない) |

- **冪等・副作用なし**: git は読み取りのみ (`rev-parse`/`show`/`status`)。解答・キャッシュ・設定・git の作業ツリーには一切書かない。
- **オフライン部分**: ローカル判定はネットワーク不要 (git のみ)。リモート判定だけが要件 050 と同じくネットワークを要する。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/selfupdate/selfupdate.go` | `LocalSource` 型と `ReadLocalSource(ctx)`、`LocalUpdate(cur, local)`、`RemoteState`/`ClassifyRemote(cur, latest)` を追加。`Available`/`Install`/`ResolveLatest` は不変 |
| `internal/selfupdate/selfupdate_test.go` | `LocalUpdate` / `ClassifyRemote` のユニットテストを追加 |
| `cmd/atcoder/update.go` | `--check` 分岐を 3 基準点 + 2 判定の表示に書き換え。`describeLocal` ヘルパ追加。`--local` / 既定 `update` の分岐は不変 |
| `fixtures/run.sh` | 既存の `update --check (proxy off → exit 1)` がローカル判定経路も通る (exit 1 のまま)。追加 fixture は不要 |
| `docs/tools/usage/update.md` | `--check` の新しい出力 (installed/local/remote + 2 判定) を反映 |
| `docs/tools/requirements/050-atcoder-self-update.md` | 本要件への相互リンクを追記 |
| `docs/tools/todo.md` | 項目を本要件にリンク |

### `internal/selfupdate` 追加 API (素描)

```go
// LocalSource は cwd の git 作業ツリーの現在状態 (HEAD)。
type LocalSource struct {
    Revision string    // git HEAD のフル sha
    Time     time.Time // HEAD コミット日時
    Dirty    bool      // tracked に未コミット変更があるか
    Known    bool      // cwd を作業ツリーとして読めたか
}

// ReadLocalSource は cwd で git を読み、作業ツリーの HEAD 版を返す。
// リポジトリ外 / git 不在 / 失敗時は Known=false (エラーにしない)。
func ReadLocalSource(ctx context.Context) LocalSource

// LocalUpdate は installed (cur) と作業ツリー (local) を比べ、
// `--local` で入れ直すとバイナリが変わるか (available) と理由文字列を返す。
func LocalUpdate(cur Current, local LocalSource) (available bool, reason string)

// RemoteState は installed と remote(latest) の関係。
type RemoteState int
const (
    RemoteUpToDate       RemoteState = iota // 入れ替え不要
    RemoteInstalledNewer                    // installed の方が新しい
    RemoteUpdateAvailable                   // remote の方が新しい
    RemoteIndeterminate                     // installed unknown で比較不能
)

// ClassifyRemote は cur と latest の関係を分類する (表示専用。Available は別物)。
func ClassifyRemote(cur Current, latest Latest) RemoteState
```

## エラーハンドリング

| 状況 | 動作 | exit |
|---|---|---|
| 未知フラグ | usage 表示 | 2 |
| `--check`・リモート解決成功 (更新有無問わず) | 3 基準点 + 2 判定を表示 | 0 |
| `--check`・リモート解決失敗 | local 行 + local 判定を出し、リモートエラーを stderr | 1 |
| ローカル git 読み取り失敗 | local 行を n/a 表示し継続 (エラーにしない) | 上記に従う |

- exit code 規約を踏襲: フラグ誤り = 2、リモート解決失敗 = 1、成功 = 0。**ローカル git の失敗は exit code を変えない** (n/a 表示で握る)。

## 非機能要件

- **既存非破壊**: `version` / `update` / `update --local` の挙動・exit code は不変。`Available`/`Install`/`ResolveLatest` のシグネチャと動作も不変。`--check` の exit code 契約 (成功 0 / リモート失敗 1) も維持。
- **依存ゼロ追加**: 標準 `os/exec` で `git` を呼ぶのみ。go.mod は変えない。
- **安全**: git は読み取り専用。解答・キャッシュ・設定・作業ツリーに書かない。
- **オフライン耐性**: ローカル判定は git だけで完結 (network 不要)。

## 将来の拡張ポイント

- `atcoder version` にも local/remote 併記。
- ローカル ⇄ origin の ahead/behind 表示 (push 漏れの可視化)。
- `--check` の終了コードで「remote 更新あり」をシグナル (要件 050 から引き継ぐ将来案)。

## 用語

- **作業ツリー HEAD**: cwd のリポジトリで現在チェックアウトしているコミット (`git rev-parse HEAD`)。未 push でもよい。
- **dirty (ローカル)**: tracked ファイルに未コミット変更がある状態 (`git status --porcelain --untracked-files=no` が非空)。未追跡ファイルは含めない。
- VCS スタンプ / pseudo-version / 中立 dir は要件 050 に準拠。

## 関連ドキュメント

- `docs/tools/requirements/050-atcoder-self-update.md` — 親要件 (`update`/`version` 本体)
- `docs/tools/usage/update.md` — 利用手引 (本要件で `--check` 出力を更新)
- `docs/tools/todo.md` — 上位ロードマップ
