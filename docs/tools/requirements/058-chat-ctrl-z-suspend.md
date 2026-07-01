# chat / start TUI の Ctrl+Z サスペンド 要件定義

## 概要

`atcoder test --interactive` / `atcoder start` の TUI (chat および watch+chat 分割画面) で **Ctrl+Z** を押したら、プロセスをサスペンド (SIGTSTP) してシェルにジョブとして戻せるようにする。シェルの慣習どおり `fg` で再開、`jobs` で一覧、`bg` でバックグラウンド継続ができる。

## 背景・目的

- chat / start の TUI は端末を占有する。手元で別コマンドを叩きたくなったとき、いまは `Ctrl+D` 連打で chat を畳むしかなく、戻ると会話セッションが失われる。
- Unix シェルでは Ctrl+Z (`SIGTSTP`) で前面ジョブを一時停止し `fg` で復帰するのが標準作法。TUI でもこれが効けば「ちょっと抜けて戻る」がコストゼロになる。
- bubbletea は altscreen 破壊を避けるため Ctrl+Z を**自動ではサスペンドに変換しない** (公式: `tea.Suspend` を明示的に返す設計)。本要件はその配線を入れるだけで、独自のシグナル処理は足さない。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 対象 TUI | chat (`internal/ui/chat.go`) と watch+chat 分割画面 (`internal/ui/startsplit.go`) | progress reporter 等の他 TUI |
| キー | `Ctrl+Z` = サスペンド | — |
| モード | chat の insert / command / builder、分割画面の通常 / 詳細表示中、いずれでも有効 | — |
| 再開 | シェルの `fg` (bubbletea が端末復元 + 再描画を自動実行) | — |
| 子プロセス | 解答プロセスは kill しない (プロセスグループ全体が停止し、`fg` で一緒に再開) | — |
| Windows | `suspendSupported=false` のため no-op (押しても何も起きない) | — |

### 境界 (他機能との分担)

- Ctrl+C (中断・再起動 / 要件 025) と Ctrl+D (リセット・2回で終了 / 要件 051) は不変。Ctrl+Z はそのいずれとも独立で、武装中の Ctrl+D は他キー同様に解除される。
- 端末の解放・復元・再描画は bubbletea の `Program.suspend()` / `RestoreTerminal()` に委ねる。`RestoreTerminal` は altscreen なら再入で、非 altscreen なら `repaintMsg` で再描画を自動発火するので、本機能側で `ResumeMsg` を明示処理する必要はない。

## CLI 仕様

フラグ追加なし。chat / start の TUI 待機中に以下が効く:

| キー | 動作 |
|---|---|
| `Ctrl+Z` | プロセスをサスペンド (SIGTSTP)。シェルに戻り `fg` で再開 |

ヘルプ文言 (chat の placeholder / 分割画面の最下部ヘルプ) に `Ctrl+Z でサスペンド` を追記する。

### 処理ステップ

1. chat の `Update` の `tea.KeyMsg` ハンドラ冒頭 (Ctrl+D 武装解除の直後、モード分岐より前) で `tea.KeyCtrlZ` を捕捉し、`tea.Suspend` を Cmd として返す。これにより insert / command / builder すべてのモードで有効。
2. 分割画面 `startSplitModel.Update` の `tea.KeyMsg` 冒頭 (詳細表示の横取りより前) でも `tea.KeyCtrlZ` を捕捉して `tea.Suspend` を返す。詳細表示中でも有効。
3. bubbletea が `SuspendMsg` を受けて `suspendSupported` なら `Program.suspend()` を実行: 端末を解放 → プロセスグループに SIGTSTP → (`fg` 時) 端末復元 + 再描画。

### 出力イメージ

```
» (chat 入力中) … Ctrl+Z を押す
[1]+  Stopped                 atcoder start abc457 --task d
$ jobs
[1]+  Stopped                 atcoder start abc457 --task d
$ fg
atcoder start abc457 --task d        # ← 画面が再描画され会話を継続
```

## 動作仕様

| 状況 | 動作 |
|---|---|
| insert モードで Ctrl+Z | サスペンド |
| command (`:`) / builder モードで Ctrl+Z | サスペンド (モード状態は保持。`fg` でそのまま継続) |
| 分割画面 通常表示で Ctrl+Z | サスペンド |
| 分割画面 詳細表示中 (Ctrl+G 中) で Ctrl+Z | サスペンド (詳細表示状態は保持) |
| Ctrl+D 武装中に Ctrl+Z | 武装は解除され、サスペンドのみ実行 (chat 終了はしない) |
| 解答の子プロセスが走行中に Ctrl+Z | 子も含めプロセスグループ全体が停止。`fg` で一緒に再開 |
| Windows | no-op (`suspendSupported=false`)。クラッシュしない |

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/ui/chat.go` | `Update` の `tea.KeyMsg` 冒頭で `tea.KeyCtrlZ` → `tea.Suspend`。placeholder ヘルプに `Ctrl+Z` 追記 |
| `internal/ui/startsplit.go` | `Update` の `tea.KeyMsg` 冒頭で `tea.KeyCtrlZ` → `tea.Suspend`。最下部ヘルプに `Ctrl+Z` 追記 |
| `internal/ui/chatsuspend_test.go` (新規) | Ctrl+Z が `tea.Suspend` (= `SuspendMsg`) を返すことを chat / 分割画面で固定 |
| `docs/tools/usage/start.md` / `docs/tools/usage/test.md` | キー一覧に Ctrl+Z を追記 |

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| 端末解放に失敗 (`ReleaseTerminal` エラー) | bubbletea 側で abort し、サスペンドせず継続 (TUI は壊さない) |
| Windows (サスペンド非対応) | `SuspendMsg` を受けても no-op。exit code には影響しない |

exit code 規約は不変 (引数誤り=2 / 実行時失敗=1 / 成功=0)。Ctrl+Z は終了経路ではない。

## 非機能要件

- **既存非破壊**: Ctrl+C / Ctrl+D / Ctrl+S / Ctrl+E / Ctrl+G / スクロール系キーの挙動は変えない。Ctrl+Z は新規の独立キー。
- **TUI 非破壊**: 端末の解放・復元・再描画は bubbletea 公式の `suspend()` / `RestoreTerminal()` に委ね、独自の termios 操作やシグナルハンドラを足さない。
- **クロスプラットフォーム**: Windows では bubbletea の `suspendSupported=false` により安全に no-op。
- **前方互換**: 将来 progress reporter 等へ横展開する際も、同じ「KeyCtrlZ → tea.Suspend」配線で足せる。

## 用語

- `SIGTSTP` — 端末から前面ジョブへ送られる一時停止シグナル (Ctrl+Z)。`fg`/`bg` で再開。
- `tea.Suspend` / `SuspendMsg` / `ResumeMsg` — bubbletea のサスペンド用 Cmd / メッセージ。

## 関連ドキュメント

- 要件 054 (`atcoder start` キーアクション) — 同じ TUI 待機中のキー操作群。
- 要件 051 (Ctrl+D リセット・2回で終了)、要件 025 (Ctrl+C 中断・再起動) — 共存する終了/中断キー。
- 要件 038 (Ctrl+E エディタ起動) — bubbletea の suspend/resume を `tea.ExecProcess` で使う前例。
