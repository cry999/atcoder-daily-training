# ADR 0004: シェル補完は CLI フレームワークを足さず手書きで実装する

- ステータス: Accepted
- 日付: 2026-06-09
- 実装: `8118b4d` (`feat(completion): add atcoder completion <shell> with dynamic completion`)
- 関連: [requirements/008-atcoder-completion.md](../requirements/008-atcoder-completion.md) / [atcoder-completion-usage.md](../atcoder-completion-usage.md)

## コンテキスト

サブコマンドが 6 つ + 多数のフラグに増え、`--task`/`--layout`/`--case` 等を毎回思い出して手打ちするフリクションが大きい。本番・練習ともに `atcoder test abc457 --task d` のように contest_id と letter を頻繁に打つので、番号や letter の打ち間違いが無駄になる。

## 決定

`atcoder completion <bash|zsh|fish>` で補完スクリプトを stdout に出力する新サブコマンドを追加する。

- **CLI フレームワーク (cobra 等) は導入しない**。標準 `flag` + 手書き dispatch を維持し、依存ゼロ追加。補完だけ手書きで足す。
- **動的補完まで**対応する: サブコマンド・フラグの静的補完に加え、`<contest>` (手元の `abc/`・`arc/`・`awc/` + fetch 済みキャッシュ)、`--task` の letter、`--layout` の値を補完。
- 動的候補は隠しヘルパ `atcoder __complete -- <words...>` に集約し、シェルスクリプトは薄いラッパに保つ。`__complete` は**常に exit 0** (補完を壊さない)。
- 読み取り専用・オフライン。CLI 本体の状態や解答ファイルに副作用なし。

## 結果

- `cmd/atcoder/completion.go` と `internal/complete/` (候補列挙 + テスト) が増えた。
- cobra を入れない代わり、フラグ表は実コード (`cmd/atcoder/*.go`) と**手書きで同期**する必要がある。フラグ追加時は `internal/complete` も更新するのが約束事 (ドリフトしうる箇所)。
- 隠し `__complete` に動的ロジックを寄せたので、シェルごとのラッパは薄く、bash/zsh/fish 差分が小さい。

## 却下した代替案

- **cobra など CLI フレームワーク導入**: 補完は自動で得られるが、既存の標準 `flag` + 手書き dispatch を全面的に置き換える大改修になり、依存も増える。補完のためだけに割に合わないと判断。
- **静的補完のみ**: サブコマンド/フラグ名だけの補完では、頻打する contest_id・letter の打ち間違いが減らない。動的候補まで踏み込む価値があると判断。
- **フラグ表のコード生成**: 手書き同期のドリフトを根絶できるが、まずは手書き + 規約で運用し、必要になれば将来導入する。
