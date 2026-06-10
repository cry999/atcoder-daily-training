# `atcoder start` 利用手引

問題に取り掛かるときの **「解答ファイルを用意 → watch テストを起動」** を 1 コマンドで済ませる。`atcoder start <contest> --task <task>` で、レイアウトに応じた解答ファイルを (無ければ) 作り、そのまま `test --watch` の編集ループに入る。

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

## 動作

1. レイアウトを解決し、解答パス (`exercise/YYYY/MM/DD/<task>.py` または `abc/<num>/<letter>.py` 等) を決める。
2. **解答ファイルを用意**: 親ディレクトリを作成し、ファイルが無ければ**空ファイル**を生成 (既存は温存)。`created:` / `solution: ... (exists)` を 1 行表示。
3. **watch の編集ループに入る**: 初回にサンプルを fetch して判定、以降は保存検知で自動再実行。画面はクリアされ最新結果だけを表示。
4. **待機中のキー操作** (下表) を受け付ける。
5. 終了:
   - `q` または `Ctrl+C` で終了 (FAIL/RE/TLE でもループは止まらない)。
   - `--until-pass` 指定時は、**サンプルが全通過した回**で自動終了 (exit 0)。

## キー操作 (watch 待機中)

各テスト実行のあとの待機中に、以下のキーが効く:

| キー | 動作 |
|---|---|
| `q` / `Ctrl+C` | watch を終了 (exit 0) |
| `i` | **インタラクティブモード** (`test --interactive` と同じ chat) を起動。抜けると watch に戻り再実行 |
| (解答を保存) | 自動再実行 |
| その他 | 無視 |

`i` で対話に入る → 抜けて watch に戻る、を何度でも繰り返せる。対話問題を試しながらサンプル判定の watch を回し続けられる。キーが効くのは**待機中だけ** (テスト実行中・chat 中は無効。chat 中は chat 側のキー操作)。端末を raw 化できない環境ではキーは無効になり、保存検知のみの watch として動く。

`start` は `new` (ファイル用意) と `test --watch` (編集ループ) + キー操作層を束ねた薄いコマンドで、新しい判定・実行ロジックは持たない。

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

- **端末 (TTY) が必要**。パイプ/リダイレクト先では watch が `exit 2` で拒否される (画面クリア前提)。
- 既存の解答ファイルは**上書きしない** (提出コードを壊さない)。`--refresh` はキャッシュのみ対象。
- 生成されるのは現状**空ファイル**。テンプレート流し込みは将来 (ロードマップ H) で差し替え予定。

## 関連

- 利用手引: [atcoder-test-usage.md](./atcoder-test-usage.md) (watch モードの詳細)
- 要件: [018-start-command.md](./requirements/018-start-command.md) / [019-start-key-actions.md](./requirements/019-start-key-actions.md) / [004-exercise-test-watch.md](./requirements/004-exercise-test-watch.md)
