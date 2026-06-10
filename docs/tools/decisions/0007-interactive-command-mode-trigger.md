# ADR 0007: インタラクティブ chat の vim 風 command モードは `Esc` で開く (`Ctrl+:` 不採用)

- ステータス: Accepted
- 日付: 2026-06-11
- 要件: [requirements/024-interactive-case-builder.md](../requirements/024-interactive-case-builder.md)
- 関連: [requirements/022-interactive-unify-quit-keys.md](../requirements/022-interactive-unify-quit-keys.md) (raw モードの端末キーの罠を確認した前例)

## コンテキスト

[024](../requirements/024-interactive-case-builder.md) で、インタラクティブ chat に「vim 風 command モード (ex-command line `:…`)」を足し、そこからケースビルダーを開く設計にした。当初の要望はトリガーを **`Ctrl+:`** にすることだった。

しかし chat の TUI は bubbletea v1.3.10 を raw モードで使っており、修飾キーの受信には端末キーコードの制約がある。実機の `key.go` を確認したところ、命名済みの Ctrl 組合せは **Ctrl+英字** と `Ctrl+@ [ \ ] ^ _ backtick` のみで、`KeyCtrlColon`/`KeyCtrlSemicolon` は存在しない。`:` (0x3A) は Ctrl のコントロールコード範囲 (0x00–0x1F) に写らないため、`Ctrl+:` を押しても端末は素の `:` (`KeyRunes`) を送るだけで、**固有キーとして判別できない**。これは [022](../requirements/022-interactive-unify-quit-keys.md) で `Ctrl+C`/`Ctrl+D` について確認した「raw モードでは自前処理しないと無反応になる/そもそも届かないキーがある」と同種の罠。

## 決定

command モードのトリガーは **`Esc`** とする。

- insert モード (既定の chat) で `Esc` → command モード。入力欄が `:` プロンプトに変わる。
- command モードで `Enter` = コマンド実行 → insert へ。`Esc` = キャンセル → insert へ。
- これは vim の「insert を抜けて (`Esc`) ex-command (`:`) を開く」流儀に忠実で、`Esc` は `KeyEsc` として確実に届き、現状 chat 内で未使用 (衝突しない)。

## 代替案 (却下)

- **`Ctrl+:` を直接トリガーにする (当初要望)**: bubbletea v1.3.10 では受信不能。kitty keyboard protocol / CSI-u を有効化すれば拾える端末もあるが、bubbletea v1 標準では非対応で**ポータブルでない**。受信不能キーへの依存は [022](../requirements/022-interactive-unify-quit-keys.md) の教訓に反する。
- **空入力行で `:` を打つと command モード**: vim 風で実装も軽いが、`:` を子プロセスへ送りたい問題 (`:` を入力に取るインタラクティブ問題) と衝突しうる。`Esc` 起点なら入力文字と曖昧にならない。
- **確実に届く別の Ctrl 組合せ (例 `Ctrl+]`)**: 受信はできるが vim の指の流儀から外れ、`Ctrl+]` は端末によって別用途 (telnet escape 等) の刷り込みがある。`Esc` のほうが mnemonic。

## 結果

- 「vim 風 command モード」という体験は保ちつつ、受信確実なキーに倒せた。`Esc` → `:` → コマンド、という遷移は vim 利用者に直感的。
- `Ctrl+:` を将来どうしても使いたくなったら、bubbletea v2 / kitty protocol 対応時に再検討する余地を残す (本 ADR を更新)。
- `Ctrl+D` = chat 終了 ([022](../requirements/022-interactive-unify-quit-keys.md)) / `Ctrl+C` = プログラム中断・再起動 ([025](../requirements/025-interactive-ctrl-c-interrupt.md)) は不変。`Esc` はそれらと独立した第 3 のキーとして command モードに割り当てる。
