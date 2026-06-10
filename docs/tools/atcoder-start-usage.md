# `atcoder start` 利用手引

問題に取り掛かるときの **「解答ファイルを用意 → 対話 + watch を同時起動」** を 1 コマンドで済ませる。`atcoder start <contest> --task <task>` で、レイアウトに応じた解答ファイルを (無ければ) 作り、そのまま**上下分割画面**に入る (上 = サンプル自動判定の watch 要約、下 = 対話 chat)。両方を同時に動かし続けられる。

> 要件詳細: [requirements/018-start-command.md](./requirements/018-start-command.md)

## コマンド

```
atcoder start <contest> --task <task> [--until-pass] [--refresh] [-d] [-s] [-j <n>] [--timeout <dur>] [--tolerance <eps>] [--layout <auto|abc|exercise>]
```

| 引数 / フラグ | 説明 |
|---|---|
| `<contest>` | コンテスト ID (例 `abc457`) |
| `--task <task>` | タスク ID または短縮形 (`d` → `<contest>_d`)。必須 |
| `--until-pass` | **サンプルが全通過したら watch を終了** (exit 0)。未指定なら `Ctrl+C` まで継続 |
| `--refresh` | 初回のみサンプルを再取得 |
| `-d` / `-s` / `-j` / `--timeout` / `--tolerance` | `test` と同じ。各 watch 実行にそのまま渡す |
| `--layout <auto\|abc\|exercise>` | 解答ファイル配置。既定は `--layout` > `ATCODER_LAYOUT` > config > auto |

## 動作 — 上下分割画面

1. レイアウトを解決し、解答パス (`exercise/YYYY/MM/DD/<task>.py` または `abc/<num>/<letter>.py` 等) を決める。
2. **解答ファイルを用意**: 親ディレクトリを作成し、ファイルが無ければ**空ファイル**を生成 (既存は温存)。`created:` / `solution: ... (exists)` を 1 行表示。
3. **上下分割画面に入る**。**chat と watch を同時に動かし続ける**:
   - **上ペイン = watch 要約**: 起動時に 1 回サンプルを判定し、以降は**保存検知のたびに自動で再判定**。`✓ PASS 3/4` / `✗ FAIL 1/4  fail: 02` のようなコンパクト要約を出す (diff は出さない)。
   - **下ペイン = 対話 chat**: `test --interactive` と同じ chat。**解答は最初に入力を送った瞬間に起動** (遅延起動)、入力ボックスに 1 行 → `Enter` で送信、子の出力は届き次第表示。auto-restart 付きなので子が終了しても閉じず、**次の入力で再実行**する (入力を読まず即終了する解答でも無限ループにならない)。
4. 編集 → 保存すると、**上ペイン (サンプル再判定) と下ペイン (chat を最新コードで reload) の両方**が新しいコードを反映する (`test --interactive` の watch-reload と同じ)。
5. 終了:
   - `Ctrl+C` または `Ctrl+D` で全体を終了 (exit 0)。
   - `--until-pass` 指定時は、**上ペインのサンプルが全通過した回**で自動終了 (exit 0)。

### キー操作

| キー | 動作 |
|---|---|
| 文字入力 + `Enter` | 下ペインの chat に送信 (子の stdin へ) |
| `↑` / `↓` | chat の入力履歴 |
| `Ctrl+S` | **提出準備** (`test --submit` 相当: 解答をクリップボードへコピー + 提出ページをブラウザで起動)。子は止めず chat に留まり、結果を 1 行表示。**実提出 (POST) はしない** |
| `Ctrl+D` / `Ctrl+C` | 全体を終了 (exit 0) |
| (解答を保存) | 上ペイン (watch) を自動再判定 + 下ペインの chat を最新コードで reload |

> `Ctrl+S` の提出準備は**サンプル全通過を待たない** (`test --submit` のゲートと違い、対話中はバッチ判定が走っていないため)。提出前に確認したいときは上ペインのサンプル結果を見るか、一度抜けて `atcoder test <contest> --task <task> --submit` を使う。

`start` は `new` (ファイル用意) と watch (サンプル自動判定) と chat (対話) を**1 画面に合成**した薄いコマンドで、新しい判定・実行ロジックは持たない。

## 例

```sh
# 当日の演習として abc457_d に着手 (exercise レイアウト)
atcoder start abc457 --task d
# → created: exercise/2026/06/11/abc457_d.py  のあと watch ループへ

# ABC 本番中、abc/ レイアウトに着手し、通ったら自動で抜ける
atcoder start abc457 --task d --layout abc --until-pass
# → created: abc/457/d.py  …編集 → 保存 → 全 PASS で自動終了

# 既にファイルがある問題に watch だけ掛け直す
atcoder start abc457 --task d
# → solution: exercise/.../abc457_d.py (exists)  のあと watch ループへ
```

## exit code

| code | 意味 |
|---|---|
| `0` | `Ctrl+C` で終了、または `--until-pass` で全通過終了 |
| `1` | ディレクトリ作成 / ファイル生成の失敗 |
| `2` | 引数誤り (`--task` 欠落・不正レイアウト)、または **非 TTY** (watch は端末必須)。※非 TTY でも解答ファイルの作成は先に行われる |

## 注意

- **端末 (TTY) が必要**。パイプ/リダイレクト先では `exit 2` で拒否される (分割画面 TUI 前提)。
- 既存の解答ファイルは**上書きしない** (提出コードを壊さない)。`--refresh` はキャッシュのみ対象。
- 生成されるのは現状**空ファイル**。テンプレート流し込みは将来 (ロードマップ H) で差し替え予定。

## 関連

- 利用手引: [atcoder-test-usage.md](./atcoder-test-usage.md) (watch モードの詳細)
- 要件: [018-start-command.md](./requirements/018-start-command.md) / [019-start-key-actions.md](./requirements/019-start-key-actions.md) / [023-start-split-screen.md](./requirements/023-start-split-screen.md) / [004-exercise-test-watch.md](./requirements/004-exercise-test-watch.md)
