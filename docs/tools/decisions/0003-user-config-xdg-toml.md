# ADR 0003: ユーザ設定は XDG_CONFIG_HOME の TOML 1 ファイルに置く

- ステータス: Accepted
- 日付: 2026-06-09
- 実装: `8108a82` (`feat(test): apply diff side-by-side default from a user config file`)
- 関連: [requirements/007-atcoder-config.md](../requirements/007-atcoder-config.md) / [atcoder-test-usage.md](../atcoder-test-usage.md) の設定ファイル節

## コンテキスト

diff を side-by-side で見たい人は毎回 `atcoder test ... -s` を付ける必要がある。好みの表示・並列度・許容誤差などは「いつも同じ値」になりがちで、毎回フラグで渡すのは摩擦が大きい。個人の既定値を 1 か所に書いておければ、`atcoder test <contest> --task d` だけで好みの挙動になる。コマンドラインで明示したフラグはその場で優先したい (一時上書き)。

## 決定

ユーザ設定ファイルの機構を導入し、第一項目として `test` の side-by-side 既定値を読む。

- 置き場所は **`$XDG_CONFIG_HOME/atcoder-daily-training/config.toml`** (fallback `~/.config/...`)。キャッシュ (`XDG_CACHE_HOME` 配下の `atcoder-tools/`) とは別軸。
- 形式は **TOML** (既存 meta/contest と同じ `BurntSushi/toml`)。サブコマンドごとにセクションを切る (`[test]`)。**未知キー/セクションは無視**して前方/後方互換を保つ。
- 第一項目は **`[test] side_by_side`** のみ。機構を最小の 1 項目で確立し、項目追加は struct にフィールドを足すだけの定型作業にする。
- 優先順位は **`flag > config > default`**。flag のデフォルト値に config 値を流し込むことで実現する。`--side-by-side=false` で config の `true` をその回だけ OFF にできる。
- config 不在は正常 (全デフォルト)。**パース失敗のときだけ exit 2**。

## 結果

- `internal/config/` (スキーマ・XDG パス解決・Load) が増え、`cmd/atcoder/test.go` が config 値を `-s` の flag デフォルトに反映する。
- 「flag のデフォルトに config を流し込む」方式は、env 層を挟まない既定値には簡潔。一方、env→config→default のように途中段が要る設定 (レイアウト等) はこの方式に乗らず別解決 (専用の resolve 関数) が要る (下記備考)。
- `internal/cachepath` (キャッシュ配置) と対をなすユーザ設定層。XDG 解決ロジックは将来共通化の余地。

> 備考: レイアウト既定値 (`ATCODER_LAYOUT` env + `layout` キー + `atcoder layout` サブコマンド) はこの設定層を拡張し、env 層を挟む別解決 (`layout.Resolve`) と書き込み (`config.Save`) を足す予定。実装が main に入った時点で ADR 化する。

## 却下した代替案

- **リポジトリ内設定ファイル**: H (テンプレート連携) で「リポジトリ内 vs XDG」を議論したが、本項目は**個人既定値**なので XDG_CONFIG_HOME を採用 (リポジトリにコミットしたくない好み設定)。
- **環境変数で既定値**: 表示の好み程度に環境変数を増やすのは管理が煩雑。設定ファイル 1 か所に集約する方が見通しが良い。
