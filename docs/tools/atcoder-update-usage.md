# `atcoder update` / `atcoder version` 利用手引

`atcoder` 自身を最新版に入れ替える・現在の版を確認する。このツールのソースはこの GitHub リポジトリ自身なので、最新版の取得・インストールは Go ツールチェインに委譲する (`go install …/cmd/atcoder@latest`)。バージョンは Go が実行ファイルに自動で埋め込む VCS 情報 (コミット sha・日時) で識別し、**git タグは使わない**。

> 要件詳細: `docs/tools/requirements/013-atcoder-self-update.md`

## コマンド

```
atcoder version
atcoder update [--check]
```

| コマンド | 動作 |
|---|---|
| `atcoder version` | いま入っている版 (短縮コミット sha・コミット日時・dirty) を表示。**オフライン**で動き副作用なし |
| `atcoder update` | 最新版を確認し、現在版と違えば `go install …@latest` で入れ替える |
| `atcoder update --check` | 確認だけ行い、**インストールはしない** |

## 前提

- **`go` コマンドが `PATH` 上にあること。** 更新は go ツールチェインに委譲する。
- **ネットワークが要るのは `update` と `--check` のみ** (go module proxy / GitHub にアクセス)。`atcoder version` はオフラインで動く。
- インストール先は `go install` の規定 (`$GOBIN` または `$GOPATH/bin`)。`atcoder` がそこから動いている前提 (= 既に `PATH` 上にある)。
- AtCoder には一切アクセスしない (`login`/`status` とは無関係)。`GOPROXY`/`GOBIN` 等の go 環境変数はそのまま尊重する。

## 使用例

```
$ atcoder version
atcoder 44f73cc537c7 (2026-06-09T08:44:44Z)

$ atcoder update --check
  current  abc1234abc12 (2026-06-05T09:00:00Z)
  latest   44f73cc537c7 (2026-06-09T08:44:44Z)
  update available — run `atcoder update`

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

- 版は Go の **buildvcs** (`go build`/`go install` が自動で埋め込む VCS 情報) を `runtime/debug.ReadBuildInfo()` で読む。`go install ./cmd/atcoder` した通常のチェックアウト由来のバイナリなら、コミット sha・日時・dirty フラグが出る。
- `go run` で実行した場合や、git の linked worktree など VCS 情報が埋め込まれない状況では `unknown (no VCS build info)` と表示される (それでも `version` は exit 0、`update` は最新版を示して入れ替えを続行する)。
- 最新版は module proxy が返す pseudo-version (`v0.0.0-<日時>-<短縮sha>`) で、その末尾 sha と現在の sha・コミット日時を比べて更新の要否を判定する。

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

- [requirements/013-atcoder-self-update.md](./requirements/013-atcoder-self-update.md) — 要件定義
- [requirements/006-rename-cli-to-atcoder.md](./requirements/006-rename-cli-to-atcoder.md) — `go install ./cmd/atcoder` 前提
- [atcoder-completion-usage.md](./atcoder-completion-usage.md) — `version`/`update` も補完対象
