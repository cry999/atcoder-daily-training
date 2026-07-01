# interactive chat の Ctrl+D を「1回目=リセット / 2回連続=終了」に変更 要件定義

## 概要

interactive chat (`test --interactive` / `start` 分割画面の下ペイン) の **`Ctrl+D` の挙動を二段階**にする。**1 回目の `Ctrl+D` = プログラムをリセット** (走っている子を kill して新プロセスで再起動。chat には留まる = 現状の `Ctrl+C` / `restart()` 相当)、**2 回連続の `Ctrl+D` = chat 自体を終了** (子を kill して quit)。「連続」は、2 つの `Ctrl+D` の間に**他のキー入力が一切挟まらない**ことを指す (Enter 送信・文字入力・`↑`/`↓`・`Ctrl+C`・`Ctrl+S`・`Esc` 等が挟まればカウントは 0 に戻る)。`Ctrl+C` (中断・再起動, 要件 025) は据え置く。

これは要件 021 (`Ctrl+D`=終了) / 022 (`Ctrl+C`・`Ctrl+D` を終了に統一) / 025 (`Ctrl+C`=中断再起動に再分離) に続く `Ctrl+D` セマンティクスの更新で、**021/022 の「`Ctrl+D` 単押しで即終了」を本要件が置き換える**。

## 背景・目的

- 現状 `Ctrl+D` は**単押しで即 chat 終了**。手が滑って `Ctrl+D` を押すと対話セッションが消えてしまう。一方 `Ctrl+C` は中断・再起動 (要件 025)。
- 「`Ctrl+D` 一発で終了」は誤爆しやすい。1 回目は**有用かつ非破壊な操作 (プログラムのリセット)** に割り当て、終了は**もう一度押す明示操作**に格上げしたい (REPL の「終了は 2 回押し」に近いが、1 回目が無動作ではなく useful action になっているのが違い)。
- リセット自体は `Ctrl+C` と同じ `restart()` を流用するだけなので実装は薄い。新規は「連続押下の状態 1 つ」と分岐のみ。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 対象キー | insert モードの `Ctrl+D` | — |
| 1 回目 | `restart()` でリセット (子 kill→再 spawn) + 「もう一度で終了」を武装 | リセット内容のカスタム |
| 2 回連続 | chat を終了 (子 kill → `tea.Quit`) | — |
| 連続の定義 | 間に他のキー入力が無いこと。出力到着・watch reload 等の**非キー**メッセージは武装を解かない | — |
| `Ctrl+C` | **据え置き** (中断・再起動, 要件 025)。単押しの即リセット手段として残す | — |
| 対象モード | insert モードのみ。command (`:`) / builder モード (要件 024) は `updateCommand`/`updateBuilder` が横取りするので不変 | — |

### `Ctrl+C` を残す理由 (棲み分け)

`Ctrl+C` = いつでも単押しで中断・再起動 (要件 025)。`Ctrl+D` = 1 回目リセット・2 回連続で終了。両方リセットになるが役割は異なる:

- `Ctrl+C`: 「**走っているプログラムを今すぐ止めてやり直す**」即時操作 (終了はしない)。
- `Ctrl+D`: 「**もう終わる**」意図の guarded quit。1 回目は副作用としてリセットしつつ「次でほんとに終了」を予告し、2 回目で閉じる。

`Ctrl+D` を消す/no-op にすると raw モードで無反応になり「終了手段が分かりにくい」ので、`Ctrl+C` は単押しリセットの確実な口として温存する。

## CLI 仕様

新フラグ・新サブコマンドは**増やさない**。insert モードのキー挙動が変わるだけ。

### insert モードのキー (変更分)

| キー | 変更前 | 変更後 |
|---|---|---|
| `Ctrl+D` (1 回目) | chat 終了 | **プログラムをリセット** (子 kill→再起動、chat 残留) + 「もう一度 `Ctrl+D` で終了」を画面に表示・武装 |
| `Ctrl+D` (2 回連続) | (同上、毎回終了) | **chat 終了** (子 kill → quit) |
| `Ctrl+C` | 中断・再起動 (不変) | 中断・再起動 (不変)。押すと `Ctrl+D` の武装は解ける |
| 他キー (`Enter`/文字/`↑`/`↓`/`Ctrl+S`/`Esc`) | — | `Ctrl+D` の武装を解く (連続カウントを 0 に戻す) |

### 処理ステップ (`Ctrl+D` 押下時, insert モード)

1. `KeyMsg` 受信の先頭で、直前が `Ctrl+D` だったか (`wasArmed`) を退避し、武装フラグを**一旦クリア** (どのキーでもまずクリア)。
2. `Ctrl+D` case:
   - `wasArmed == true` (= 2 回連続) → 子が居れば kill → `tea.Quit` で chat 終了。
   - `wasArmed == false` (= 1 回目):
     - 再起動可能 (`spawn != nil`) → `restart()` を呼びリセット。`(プログラムをリセットしました — もう一度 Ctrl+D で chat を終了)` を表示。武装フラグを立てる。
     - 再起動不可 (`spawn == nil`) → リセットできないので、`(もう一度 Ctrl+D で chat を終了)` を表示し武装のみ。
3. 他のキー (`Enter`/文字/`Ctrl+C`/`Ctrl+S`/`↑`/`↓`/`Esc` 等) は手順 1 のクリアで武装が解けるため、再び `Ctrl+D` を押すと 1 回目からになる。

### 出力イメージ (chat 画面内)

```
> 3
< 6
(プログラムをリセットしました — もう一度 Ctrl+D で chat を終了)   ← 1 回目の Ctrl+D
─── session #2 ───
(入力を送ると…)
                                                              ← ここで 2 回目の Ctrl+D を押すと chat 終了
```

## 動作仕様

| 項目 | 挙動 |
|---|---|
| 連続判定 | 2 つの `Ctrl+D` の間に**キー入力**が無いこと。子の出力到着・watch reload・スピナー tick 等の**非キー** msg は武装を解かない (= 出力が来ても 2 回目で終了できる) |
| リセット内容 | 既存 `restart()` (kill→wait→spawn、`sessionN` を進め epoch を更新)。`Ctrl+C` のリセットと同一 |
| 遅延起動 (子未起動) | 1 回目: `spawn != nil` なら `restart()` が新規 spawn しつつ武装。`spawn == nil` なら武装のみ。2 回目: 終了 |
| auto-restart 中 | 不変。リセット・武装・終了の挙動は auto-restart の ON/OFF に依らない |
| command / builder モード | 不変 (要件 024 の `updateCommand`/`updateBuilder` が横取り)。モードに入る `Esc` はキー入力なので武装を解く |
| `Ctrl+C` | 不変 (要件 025)。押下で `Ctrl+D` 武装は解ける |
| 終了コード | chat 終了は従来どおり (子の最終結果に依存。`Ctrl+D`×2 自体は exit 0 相当) |
| 解答ファイル | リセットは子プロセスのみ。解答・キャッシュには触れない |

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/ui/chat.go` | `chatModel` に連続押下フラグ (`ctrlDArmed bool`) を追加。`KeyMsg` 先頭で `wasArmed` を退避しフラグをクリア。`KeyCtrlD` case を「1 回目=`restart()`+武装 / 2 回連続=quit」に書き換え。placeholder / 初期 info の `Ctrl+D` ヒントを更新 |
| `internal/ui/chatctrld_test.go` (新規) | 状態機械のユニットテスト: 1 回目で `restart` 相当 (子 kill→running 再設定) + 武装、2 連続で `tea.Quit`、間に他キー (`Enter`/`Ctrl+C` 等) を挟むと武装が解けて 1 回目に戻る、出力 msg では武装が解けない |
| `internal/ui/startsplit.go` | 変更不要 (`default:` 分岐が `KeyMsg` を chat に委譲。`Ctrl+D`×2 の `tea.Quit` がそのまま分割画面全体の終了に伝播する) — 確認のみ |
| `docs/tools/usage/test.md` | 対話モードの `Ctrl+D` 説明を「1 回でリセット・2 回連続で終了」に更新 |
| `docs/tools/usage/start.md` | 分割画面キー表の `Ctrl+D` 行を同様に更新 |
| `docs/tools/todo.md` | 本項目を追加し ✅ DONE。要件 021/022/025 との関係を明記 |

### 状態フィールド (`internal/ui/chat.go`)

```go
// ctrlDArmed は直前のキーが Ctrl+D だった (= 次の Ctrl+D で chat 終了) ことを表す。
// KeyMsg 受信のたびに先頭でクリアし、Ctrl+D の 1 回目だけ立て直す。
ctrlDArmed bool
```

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| `spawn == nil` で 1 回目 `Ctrl+D` | リセット不可。武装のみ (メッセージ提示) → 2 回目で終了 |
| リセット (`restart()`) が spawn 失敗 | 既存 `restart()` のエラー処理に従う (spawn 失敗行を表示)。武装は維持してよい (2 回目で終了できる) |
| (注) chat はキー操作の TUI なので、これらは exit code ではなく画面内の状態・1 行で表現する。chat 終了自体の終了コードは本変更で変わらない |

## 非機能要件

- **既存非破壊**: `Ctrl+C` (中断再起動)・`Enter` 送信・履歴・`Ctrl+S` (提出準備)・watch reload・command/builder モードは不変。変わるのは insert モードの `Ctrl+D` のみ。
- **誤爆耐性**: 終了を 2 連続押下に格上げし、1 回目は非破壊なリセットに割り当てる。
- **状態は 1 つ**: `ctrlDArmed` のみ。`KeyMsg` 先頭クリア + `Ctrl+D` 再武装の対称な実装で、武装が漏れ残らない。
- **前方互換**: モード (024) と独立。将来 command モードに `:reset` 等を足しても干渉しない。

## 将来の拡張ポイント

- 連続押下のタイムアウト (一定時間で武装解除) — 現状は「他キーで解除」のみで時間では解かない。
- `Ctrl+C` を「中断のみ」、`Ctrl+D` を「リセット/終了」と明確に役割分離する案内の改善。

## 用語

- **リセット (reset)**: 走っている子プロセスを kill して新プロセスで再起動すること (`restart()`)。chat 自体は閉じない。
- **武装 (armed)**: 直前が `Ctrl+D` で、次の `Ctrl+D` が chat 終了になる状態 (`ctrlDArmed`)。
- **insert / command / builder モード**: chat の入力モード (要件 024)。本変更は insert モードのみ対象。

## 関連ドキュメント

- `docs/tools/requirements/021-interactive-ctrl-d-quit.md` (`Ctrl+D`=終了。本要件が単押し即終了を置き換える)
- `docs/tools/requirements/022-interactive-unify-quit-keys.md` (`Ctrl+C`/`Ctrl+D` を終了に統一した経緯)
- `docs/tools/requirements/025-interactive-ctrl-c-interrupt.md` (`Ctrl+C`=中断再起動。本要件で据え置き)
- `docs/tools/requirements/024-interactive-case-builder.md` (command/builder モード。本変更は insert モードのみ)
- `docs/tools/usage/test.md` / `docs/tools/usage/start.md` (キー説明の更新先)
