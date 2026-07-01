# `atcoder commit` 利用手引

当日 (`exercise/YYYY/MM/DD/`) の演習成果をひとまとめにコミットするためのショートカット。普段「解いて、テストして、コミット」の流れを 1 コマンドで締められる。

## コマンド

```
atcoder commit
```

引数・フラグは無い。常に **当日のローカル日付** 配下のディレクトリを対象とする。

## 挙動

1. `exercise/YYYY/MM/DD/` の存在確認。無ければエラー終了。
2. `git add -A -- exercise/YYYY/MM/DD/` を実行 (新規ファイル・変更・**削除も含めて** index に反映)。
3. 対象ディレクトリ配下に staged 変更が **一つも無ければ** エラー終了 (exit 1)。
4. `git commit -m "exercise: YYYY-MM-DD" -- exercise/YYYY/MM/DD/` を実行。
   - pathspec を付けているので、当日ディレクトリ外に staged されている変更は **index に残ったままコミットされない**。

> 補足: テスト用のサンプル I/O (`tests/NN.in NN.out`) と meta.toml は `$XDG_CACHE_HOME/atcoder-tools/` 配下に保存されているため、本コマンドのコミット対象には含まれない (= コミットは解答ファイルだけが軽量に乗る)。

## コミットメッセージ

固定で `exercise: YYYY-MM-DD` (例: `exercise: 2026-06-06`)。リポジトリの既存スタイル ([recent commits](https://github.com/cry999/atcoder-daily-training/commits/main)) に合わせている。

カスタマイズが必要なら、このコマンドを使わず手で `git commit -m "..."` する想定。

## exit code

| code | 意味 |
|---|---|
| `0` | コミット成功 |
| `1` | 当日ディレクトリ無し、ステージ対象無し、`git` の失敗 |
| `2` | 引数エラー (現状なし) |

## 想定する流れ

```sh
# 1日の演習を書く
go run ./cmd/atcoder new              # 当日の exercise/YYYY/MM/DD/ を作成
vim exercise/2026/06/06/abc330_d.py    # 解く
go run ./cmd/atcoder test abc330 -c d # サンプルを fetch + 動作確認

# まとめてコミット
go run ./cmd/atcoder commit
# → exercise: 2026-06-06
```

## 注意

- 他のディレクトリで作業中の **staged な変更がある場合**、それらは index に残るが今回のコミットには含まれない。これは「演習だけを切り出してコミットする」設計上の意図的な挙動。
- 削除されたファイル (例: 古い `tests/` を整理した場合) も `git add -A` で拾うため、コミットに含まれる。
