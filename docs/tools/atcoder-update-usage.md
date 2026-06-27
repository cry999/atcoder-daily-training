# `atcoder update` / `atcoder version` 利用手引

`atcoder` 自身を最新版に入れ替える・現在の版を確認する。このツールのソースはこの GitHub リポジトリ自身なので、最新版の取得・インストールは Go ツールチェインに委譲する (`go install …/cmd/atcoder@latest`)。バージョンは Go が実行ファイルに自動で埋め込む VCS 情報 (コミット sha・日時) で識別し、**git タグは使わない**。

> 要件詳細: `docs/tools/requirements/050-atcoder-self-update.md`

## コマンド

```
atcoder version
atcoder update [--check | --local]
```

| コマンド | 動作 |
|---|---|
| `atcoder version` | いま入っている版 (短縮コミット sha・コミット日時・dirty) を表示。**オフライン**で動き副作用なし |
| `atcoder update` | 最新版を確認し、現在版と違えば `go install …@latest` で入れ替える (GitHub に push 済みの最新) |
| `atcoder update --check` | 確認だけ行い、**インストールはしない**。インストール済み版を **リモート (`@latest`) とローカル作業ツリー (git HEAD) の両方** と比べる |
| `atcoder update --local` | `@latest` ではなく **cwd の `./cmd/atcoder`** を `go install` する (手元の作業ツリーをそのまま入れる) |

`--check` と `--local` は併用不可 (exit 2)。

### `--check` (リモート / ローカル両方の最新確認)

`atcoder update --check` は **3 つの基準点** を並べ、**2 つの判定** を出す:

- `installed` — いま入っているバイナリの版 (埋め込み VCS / pseudo-version)。
- `local` — cwd の git 作業ツリーの HEAD (sha・日時・dirty)。リポジトリ外なら `n/a`。
- `remote` — GitHub に push 済みの `@latest` (= origin デフォルトブランチ HEAD)。

判定は 2 軸:

- `remote:` — installed が **リモート** より古いか (`update available`) / 最新か / **installed の方が新しいか** (`up to date (installed is newer than origin)`)。
- `local:` — installed が **手元の作業ツリー** と一致するか / `update --local` で入れ直すと変わるか (`rebuild available`、理由付き)。

```
$ atcoder update --check        # 手元で dirty ビルドを入れている / 未 push が手元に進んでいる
  installed  69d5e73 (2026-06-25T21:59:30Z) dirty
  local      69d5e73 (2026-06-25T21:59:30Z) dirty
  remote     ca3f863 (2026-06-25T21:06:48Z)

  remote: up to date (installed is newer than origin)
  local:  rebuild available — run `atcoder update --local` (working tree has uncommitted changes)
```

- **ローカル判定はオフライン** (git だけ)。リモート解決に失敗 (network/proxy/`go` 不在) しても `installed` / `local` 行と `local:` 判定までは表示し、リモートのエラーを stderr に出して **exit 1**。
- `local` の dirty は **tracked ファイルの未コミット変更** のみ (`git status --porcelain --untracked-files=no`)。`exercise/` 等の未追跡な練習解答は dirty に数えない。
- これにより、`go install ./cmd/atcoder` 直後のように **installed の方が `@latest` より新しい** ときでも「常に update available」と誤表示せず、「installed is newer」「手元と一致 / 入れ直しで変わる」を正しく言い分けられる。

### `--local` (手元のソースから入れる)

`atcoder update` (= `@latest`) は **GitHub に push 済みのコミットまで**しか取得できないので、ローカルで作業中・未 push のコミットは反映できない。`atcoder update --local` はその穴を埋め、**いまチェックアウトしている作業ツリーを直接インストール**する:

```
$ cd ~/path/to/atcoder-daily-training   # リポジトリ内で実行する
$ atcoder update --local
  current  abc1234abc12 (2026-06-05T09:00:00Z)
  installing… go install ./cmd/atcoder
  installed from local working tree ✓
```

- **リポジトリ内 (cwd が `./cmd/atcoder` を解決できる場所) で実行すること。** モジュール外で実行すると `go install ./cmd/atcoder` が失敗する (exit 1)。
- 最新解決・proxy・ネットワークは不要 (手元のソースをビルドするだけ)。未コミットの変更もそのまま入る。
- 作業ツリーからのビルドなので、入った版は VCS スタンプ付き (`atcoder version` がコミット sha を表示する)。

## 前提

- **`go` コマンドが `PATH` 上にあること。** 更新は go ツールチェインに委譲する。
- **ネットワークが要るのは `update` と `--check` のみ** (go module proxy / GitHub にアクセス)。`atcoder version` はオフラインで動く。
- インストール先は `go install` の規定 (`$GOBIN` または `$GOPATH/bin`)。`atcoder` がそこから動いている前提 (= 既に `PATH` 上にある)。
- AtCoder には一切アクセスしない (触る外部は Go module proxy / GitHub のみ)。`GOBIN` 等の go 環境変数は尊重する。ただし **このツール自身のモジュールだけは `GOPRIVATE` に入れて proxy を介さず git remote へ直接問い合わせる** (理由は下記)。依存モジュールは通常どおり proxy + sumdb 経由。

## 使用例

```
$ atcoder version
atcoder 44f73cc537c7 (2026-06-09T08:44:44Z)

$ atcoder update --check
  installed  abc1234abc12 (2026-06-05T09:00:00Z)
  local      44f73cc537c7 (2026-06-09T08:44:44Z)
  remote     44f73cc537c7 (2026-06-09T08:44:44Z)

  remote: update available — run `atcoder update`
  local:  rebuild available — run `atcoder update --local` (local source is ahead of the installed binary)

$ atcoder update
  current  abc1234abc12 (2026-06-05T09:00:00Z)
  latest   44f73cc537c7 (2026-06-09T08:44:44Z)
  installing… go install github.com/cry999/atcoder-daily-training/cmd/atcoder@latest
  installed 44f73cc537c7 ✓

$ atcoder update            # 既に最新
  current  44f73cc537c7 (2026-06-09T08:44:44Z)
  latest   44f73cc537c7 (2026-06-09T08:44:44Z)
  already up to date (44f73cc537c7)
```

## バージョン表示について

現在版は `runtime/debug.ReadBuildInfo()` から読む。出所はインストール方法で 2 通り:

- **`go install ./cmd/atcoder`**(作業ツリーからのビルド): Go の **buildvcs** が埋め込む VCS 情報 (フルコミット sha・日時・dirty) を使う。
- **`atcoder update`**(= `go install …@latest`): 作業ツリーではなくダウンロード済みモジュールからのビルドなので VCS 情報は付かない。代わりに **モジュール版 (pseudo-version `v0.0.0-<日時>-<短縮sha>`)** から sha と日時を取り出して表示・比較する。

これにより、`update` で入れ替えた後も `version` がコミットを表示でき、`update --check` が「最新」を正しく判定する (毎回 update available にならない)。`go run` 実行や linked worktree など、どちらの情報も無い状況では `unknown (no VCS build info)` と表示される (それでも `version` は exit 0、`update` は最新版を示して入れ替えを続行)。

### 最新版の解決 (proxy を介さない理由)

最新版の解決・取得は **このツール自身のモジュールを `GOPRIVATE` に入れて行う** (= proxy.golang.org を介さず git remote へ直接問い合わせる)。proxy は `@latest` を一定時間キャッシュするため、push 直後は **古いコミットを最新として返す**ことがあり、それが原因で「最新のはずが古い版がインストールされる」不具合が起きた。直接解決にすることで、常に origin のデフォルトブランチ (main) の現在 HEAD を取得する。

- 取得できるのは **GitHub に push 済みのコミットまで**。ローカルにしか無い未 push のコミットは `@latest` には現れない (push が前提)。
- 依存モジュールは `GOPRIVATE` に含めないので、通常どおり proxy + sumdb 経由 (高速・検証あり)。

## exit code

| code | 意味 |
|---|---|
| `0` | 成功 (`version` 表示・`update` の入れ替え or 既に最新・`--check` の確認完了) |
| `1` | 実行時失敗 (最新版の解決失敗 = network/proxy/`go` 不在、`go install` 失敗) |
| `2` | フラグ誤り (未知フラグなど) |

`atcoder update --check` は、更新の有無によらず **確認が成功すれば exit 0**。更新が出ているかは標準出力のテキスト (`update available` / `up to date`) で伝える。

## 注意

- 触るのは**自分自身のバイナリのみ**。解答ファイル・キャッシュ・`config.toml`・git には一切書き込まない。
- `go list -m @latest` / `go install …@latest` は中立な一時ディレクトリを cwd にして実行するため、**どの cwd からでも同じ結果**になる (リポジトリの内外を問わない)。
- proxy のキャッシュ次第で「最新」がやや古いコミットを指すことがある (GitHub への push 直後など)。

## 関連

- [requirements/050-atcoder-self-update.md](./requirements/050-atcoder-self-update.md) — 要件定義
- [requirements/059-update-local-check.md](./requirements/059-update-local-check.md) — `--check` のローカル (作業ツリー) 比較拡張
- [requirements/006-rename-cli-to-atcoder.md](./requirements/006-rename-cli-to-atcoder.md) — `go install ./cmd/atcoder` 前提
- [atcoder-completion-usage.md](./atcoder-completion-usage.md) — `version`/`update` も補完対象
