# ADR 0001: `test --watch` は mtime ポーリングで単一ファイルを監視する

- ステータス: Accepted
- 日付: 2026-06-09
- 実装: `1105a67` (`feat(test): add --watch mode to re-run on solution file changes`)
- 関連: [requirements/004-exercise-test-watch.md](../requirements/004-exercise-test-watch.md) / [docs/tools/usage/test.md](../usage/test.md) の watch 節

## コンテキスト

編集ループ中は「コードを直して保存 → ターミナルに戻って `atcoder test ...` を再実行」を何十回もくり返す。往復のたびに編集リズムが切れる。サンプルは初回 fetch 後はキャッシュにあり、2 回目以降の再実行はネットワーク不要で速いので、保存検知で自動再実行する watch ループに向いている。

## 決定

`atcoder test <contest> --task <task> --watch` (`-w`) で常駐し、解答ファイルの保存を検知して自動再実行する。

- **監視対象は解答ファイル 1 つだけ**。サンプルや自作ライブラリは監視しない (将来の拡張)。「保存=再実行」を直感的かつ誤爆なしにするため。
- **検知方式は mtime ポーリング (200ms)**。外部依存を足さない。単一ファイル監視には十分で、最小依存方針に合う。atomic save (一旦削除して書き直す) でも再出現時の mtime 変化で拾える。
- **TTY 必須**。画面をクリアして最新結果だけを再描画するため、非 TTY (パイプ/リダイレクト) では exit 2。
- 既存の並列実行 + ライブ進捗表示 (`internal/ui` の bubbletea Reporter) を各実行にそのまま再利用する。
- `--watch` + `--refresh` は**初回のみ** refresh。毎保存での再 fetch を避け rate limit を踏まない。
- 終了コードはループ結果に依存しない。FAIL/RE/TLE でもループは止めず、`Ctrl+C` での終了は exit 0。

## 結果

- `internal/watch/` (単一ファイルの mtime ポーリング) が増えた。`cmd/atcoder/test.go` に `--watch` 分岐、`internal/ui/` に画面クリア・watch ヘッダ/フッタ。
- fsnotify 等の OS イベント監視に頼らないため移植性・依存の点で楽。一方、ポーリング間隔 (200ms) 未満の高速連続保存は 1 回にまとまりうる (実用上問題なし)。
- 監視が単一ファイルなので、ライブラリ分割した解答では import 先の変更を拾えない (既知の割り切り)。

## 却下した代替案

- **fsnotify による OS ファイルイベント監視**: 依存が増え、エディタの atomic save パターンでハンドルが切れる扱いが煩雑。単一ファイルの 200ms ポーリングで十分と判断。
- **複数ファイル/ディレクトリ監視**: 「保存=再実行」の誤爆 (無関係ファイルでの再実行) を招く。まず解答 1 ファイルに限定。
