# `atcoder test` 利用手引

`atcoder` ツールの `test` サブコマンドの使い方をまとめる。`test` は解答を走らせる唯一の入口で、**既定はサンプル判定**、`--in` / `--out` / `--interactive` を付けると ad-hoc 実行・対話モードになる (旧 `atcoder run` は `test` に統合・廃止)。

仕様の詳細は [001-exercise-test.md](./requirements/001-exercise-test.md)、統一の経緯は [013-unify-test-run.md](./requirements/013-unify-test-run.md) / [ADR 0005](./decisions/0005-unify-test-run-into-test.md) を参照。

## 前提

- リポジトリルートで操作することを想定する。
- Python の実行には `<repo_root>/.venv/bin/python` を使う。Poetry で `.venv` を作成済みであること。

```sh
poetry install        # 初回のみ
```

- ツール本体は Go 製。実行は `go run ./cmd/atcoder` または事前ビルド (`go build -o atcoder ./cmd/atcoder`)。

## クイックスタート

ABC325 の問題 D を当日の演習として書いたあとに、サンプルケースでテストする。

```sh
# 1. 当日の演習ディレクトリを用意 (まだ無ければ)
go run ./cmd/atcoder new

# 2. 解答を exercise/YYYY/MM/DD/abc325_d.py として書く

# 3. テストを実行
go run ./cmd/atcoder test abc325 --task abc325_d
```

初回実行時に AtCoder の問題ページからサンプル入出力と Time Limit を取得し、以下のように **解答 (per-day) とキャッシュ (XDG)** に分けて保存する。

```
# 解答 (git 管理)
exercise/YYYY/MM/DD/
  abc325_d.py

# キャッシュ (XDG_CACHE_HOME 配下、git 管理しない)
~/.cache/atcoder-tools/abc325/abc325_d/
  meta.toml
  tests/
    01.in
    01.out
    02.in
    02.out
```

`XDG_CACHE_HOME` が設定されていればそちらが優先される。2 回目以降は保存済みのキャッシュを使うためネットワークアクセスは発生しない。**別の clone (自宅 / 職場 等) からアクセスする場合も `~/.cache/atcoder-tools/` を共有しておけば fetch 結果を使い回せる**。

## コマンド

```
atcoder test <contest> --task <task>            # 既定: DL 済みサンプルを判定
    [サンプル: -c <N[,M,...]> | --refresh | -j <n> | -w | -s]
    [ad-hoc:  --in <path>|- | --out <path>]
    [対話:    --interactive [-R | --auto-restart]]
    [共通:    -v | -d | --timeout <dur> | --tolerance <eps> | --layout <auto|abc|exercise>]
```

### 引数

> **位置引数 (`<contest>`) とフラグの順序は自由**。`atcoder test --task d abc457` も `atcoder test abc457 --task d` も等価 (フラグの前・後・間どこに置いてもよい)。`--task=d` 形や `--` 終端も使える。

| 引数 | 必須 | 説明 |
|---|---|---|
| `<contest>` | ✔ | AtCoder のコンテスト ID (例: `abc325`)。URL の `/contests/<contest>/` に対応 |
| `--task <task>` | ✔ | AtCoder のタスク ID (例: `abc325_d`)。URL の `/tasks/<task>` に対応。**短縮形**: `_` を含まない値は `<contest>_<task>` に自動展開 (例: `--task d` + `<contest>=abc325` → `abc325_d`) |
| `-v` / `--verbose` | | 各ケースで入力 (`input:`) と実際の出力 (`output:`) を表示 |
| `-d` / `--debug` | | 子プロセスに `DEBUG=1` を渡し、stdout のうち `[DEBUG]` で始まる行を比較対象から除外。除外行は `debug:` セクションに表示 |
| `-c` / `--case <N>` | | 指定したケース番号のみ実行。カンマ区切りで複数可 (`-c 1,3`)。数値は `01`, `03` のように 2 桁ゼロ埋めへ正規化。該当無しはエラー終了 |
| `-s` / `--side-by-side` | | diff を左右 2 カラムで表示 (期待出力=左、実際の出力=右) |
| `--refresh` | | テストキャッシュを無視して AtCoder から再取得 |
| `--timeout <dur>` | | 1 ケースあたりの実行制限時間を上書き。Go の duration 記法 (例: `5s`, `500ms`)。未指定なら `meta.toml.time_limit_ms` の値を使う |
| `--tolerance <eps>` | | float トークン比較の絶対/相対許容誤差 (例: `1e-9`)。未指定または `0` は既定の `1e-6` |
| `--layout <auto\|abc\|exercise>` | | 解答ファイルの配置規約。`exercise`=当日 `exercise/YYYY/MM/DD/<task>.py`、`abc`=`abc/<num>/<letter>.py`、`auto`=`abc<NNN>` なら `abc`、それ以外は `exercise`。**省略時**は `$ATCODER_LAYOUT` → `config.toml` の `layout` → `auto` の順で既定値を引く ([既定レイアウトの固定](atcoder-config-usage.md#layout-既定レイアウト)参照) |
| `-j` / `--jobs <n>` | | テストケースを並列実行する数。`0` (既定) は CPU 数 (ケース数で頭打ち)。`-j 1` で逐次 |
| `-w` / `--watch` | | 解答ファイルの保存を監視し、変更のたびにテストを自動再実行。`Ctrl+C` で終了。**端末 (TTY) が必要** |
| `--in` / `-i <path>` | | **ad-hoc モード**に切替。自前入力で 1 回実行 (`-` で stdin)。判定はしない (`--out` 併用時のみ) |
| `--out` / `-o <path>` | | **ad-hoc モード** (判定付き)。stdout を期待出力ファイルと突合せ。`--in` 省略時は stdin を読む |
| `--interactive` / `-I` | | **対話モード**。子の stdin/stdout を親に直結 (TTY なら chat TUI)。`--out` / ファイル `--in` とは併用不可 |
| `--auto-restart` / `-R` | | 対話モードの chat TUI (TTY) で、子終了後も閉じず**次の入力で再実行**する。`--interactive` 必須 (無いと `exit 2`)。非 TTY では無効 |
| `--submit` | | サンプルが**全通過したら**、解答をクリップボードへコピーし提出ページをブラウザで開く (旧 `atcoder submit`)。サンプルモード専用 |
| `--no-open` | | `--submit` 時にブラウザを開かず提出 URL を表示するだけ |

> `--in`/`--out`/`--interactive` を**明示**したときだけ ad-hoc/対話になる。付けなければ既定のサンプル判定で、stdin がパイプされていてもモードは変わらない (ad-hoc にしたいときは `--in -`)。サンプル専用フラグ (`--refresh`/`-c`/`-j`/`-w`/`-s`/`--submit`) と ad-hoc フラグの併用は `exit 2`。`--submit` と `--watch` の併用も `exit 2`。詳細は下の「モード」節と「提出準備」節。

### 解答ファイルの特定

ツールは **当日 (ローカル時刻) の `exercise/YYYY/MM/DD/<task>.py`** を解答ファイルとして使う。指定された日付の解答だけをテストする想定であり、過去日の解答は (現時点では) テストできない。

## モード: サンプル判定 (既定) / ad-hoc / 対話

`test` は入力ソースで 3 モードに分かれる。**既定はサンプル判定**で、`--in`/`--out`/`--interactive` を明示したときだけ ad-hoc / 対話に切り替わる。

| モード | トリガ | 内容 |
|---|---|---|
| サンプル判定 (既定) | フラグ無し | DL 済みサンプル群を判定 (PASS/FAIL/TLE/RE) |
| ad-hoc | `--in <path>` / `--in -` / `--out <path>` | 自前入力で 1 回実行。`--out` 指定時のみ突合せ判定 |
| 対話 | `--interactive` (`-I`) | 子の stdin/stdout を親に直結。TTY なら chat TUI |

- stdin がパイプされていてもモードは変わらない。stdin から ad-hoc 入力したいときは `--in -` を明示する。
- サンプル専用フラグ (`--refresh`/`-c`/`-j`/`-w`/`-s`) と ad-hoc フラグの併用は `exit 2`。
- 対話は `--out` ともファイル `--in <path>` とも併用不可 (`exit 2`)。`--in -` は可。

### ad-hoc 実行

```sh
# 自前ケースで動かして出力を見る (判定なし)
atcoder test abc325 --task d --in my_case.txt

# stdin から (パイプ/リダイレクト)。--in - を明示する
echo "5" | atcoder test abc325 --task d --in -
atcoder test abc325 --task d --in - < my_case.txt

# 期待出力と突合せ (1 件 judge)
atcoder test abc325 --task d --in my_case.txt --out expected.txt
```

出力ステータスは `OK` / `TLE` / `RE`。`-v` で渡した入力も表示、`-d` で `DEBUG=1`。

### 対話モード

`--interactive` (`-I`) で子プロセスと live 対話する。入力は親 stdin から読む。

- **TTY (端末から直接)**: bubbletea ベースの chat TUI。**解答プログラムは開いた時点では起動せず、最初に入力を送った瞬間に起動する** (遅延起動)。入力ボックスに 1 行 → `Enter` でその入力を送って子を起動 (既に動いていれば送信のみ)、子の出力は届き次第表示。`↑`/`↓` で入力履歴、`Ctrl+C` で**プログラムを中断して再起動** (走っている子を kill し新しいプロセスでやり直す。chat には留まる)、`Ctrl+D` で**プログラムをリセット** (1 回目。`Ctrl+C` と同じく子を kill して再起動・chat には留まる) — **続けてもう一度 `Ctrl+D` を押すと chat を終了** (子を kill して quit。子に EOF は送らない)。間に他のキーを打つと「2 回連続」のカウントは戻る。子は `PYTHONUNBUFFERED=1` 付きで起動するので `flush()` 不要。EOF まで読む batch プログラムの確認は `--in <file>` を使う。
  - **`Ctrl+S` で提出準備**: chat 中に `Ctrl+S` を押すと**提出準備** (`test --submit` 相当: 解答をクリップボードへコピー + 提出ページをブラウザで起動) を行う。子は止めず chat に留まり、結果を 1 行表示する。**実提出 (POST) はしない**。サンプル全通過を待たない (対話中はバッチ判定が走らないため。`test --submit` のゲートとは異なる)。
  - **出力タイミング表示**: 子の出力行 (`←`/`✖`/`*`) には、行頭に**直前イベント (最後に入力を送ってから、または直前の出力から) その行までの経過時間**が dim・固定幅で添えられる (`  218ms ← Query?`)。応答レイテンシと連続出力の間隔がひと目で分かる。書式は**最大単位のみ・四捨五入** (`340µs`/`218ms`/`12s`)。ただし 10,000ms 未満は `s` でなく `ms` で出す (`1100ms`、`10s`)。入力行 `→` と情報行には付かない。
  - **保存でリロード**: chat 中に**解答ファイルを保存すると自動で検知**し、実行中の子を kill して**最新ファイルで再起動**する (`(解答ファイルが更新されました — 新しいプログラムを起動します)` を出して `─── session #N ───` で仕切る)。chat を抜けずに編集→対話を回せる。別ターミナルで保存するだけでよい。
  - **出力待ちスピナー**: 入力を送ってから次の出力が返るまでの間、入力ボックスの下罫線に**スピナー (`⠹`) + 経過時間**をライブ表示する (`⠹ 430ms ────`)。応答が遅い・固まっている・入力過不足をすぐ気づける。出力が返る (または子が終了する) と消える。
- **非 TTY (パイプ/リダイレクト)**: passthrough + tee。送った各行を `> <input>` と echo してから子に転送する batch-friendly モード (厳密な交互表示は保証されない。チャットらしさが要るなら TTY か `expect`(1))。

```sh
atcoder test abc999 --task a --interactive                      # chat TUI
printf "3\nok\nok\nok\n" | atcoder test abc999 --task a --interactive
```

#### 連続実行 (`--auto-restart` / `-R`)

既定では子プロセスが終了すると chat TUI も閉じる。`--auto-restart` を付けると **子が終了しても閉じず、次に入力を送ったときに同じ解答を再実行**する。リプレイや複数ラウンドの対話問題を続けて試せる。再実行は**入力を機に**起こすので、入力を読まず即終了する解答でも無限ループにならない。

- chat を抜けるには `Ctrl+D` を**2 回連続**で押す (1 回目はプログラムのリセット = 子を kill して再起動、2 回目で chat 終了)。間に他のキーを打つとカウントは戻る。`Ctrl+C` は終了ではなく**プログラムの中断・再起動** — auto-restart 中でも「今すぐ新プロセスでやり直す」操作になる。
- `--auto-restart` は対話モード専用。`--interactive` 無しで指定すると `exit 2`。非 TTY (パイプ) では chat TUI を使わないため無効で、1 回だけ実行する。

```sh
atcoder test abc999 --task a --interactive --auto-restart       # 子が終わるたびに再実行
```

#### ケース作成 + ライブ検証 (vim 風 command モード)

chat で見つけた再現入力をその場で**追加テストケース**にできる。`Esc` で **command モード** (`:` 行) に入り、vim の ex-command のように 1 行打って `Enter` で実行する (`Esc` でキャンセル)。`Ctrl+C`/`Ctrl+D`/`Ctrl+S` は insert モードのまま不変。`:` 行では **`Tab` でコマンド名・サブトークン** (`:set verify|noverify` など) を補完できる (一意なら確定、複数候補は `:` 行直下に一覧表示。要件 [031](./requirements/031-command-mode-completion.md))。

| コマンド (別名) | 動作 |
|---|---|
| `:case` (`:c`) | **ケースビルダー**を開く。`input (.in)` ペインは現セッションで送った入力で前埋め、`expected (.out)` ペインは手入力。`Tab` でペイン切替 |
| `:w [name]` | ビルダーの内容を `tests-extra/` に保存 (`name` 省略時は連番)。保存後 `(saved tests-extra/x03)` を出して chat に戻る |
| `:set verify` / `:set noverify` | ライブ検証の on/off。ビルダーで expected を入れて閉じると自動 on |
| `:debug` (`:set debug` / `:set nodebug`) | Debug 表示 (`-d` 相当、子 stdout の `[DEBUG]` 行を別カテゴリ表示) を切替。**以降届く行に反映**され、既に出ている行は変えない |
| `:cheat` (`:help` / `:?`) | 今この画面で使える command 一覧をチートシートとして表示 (`start` 分割画面では `:task`/`:contest`/`:e` も載る) |
| `:q` | ビルダー中なら破棄して閉じる。それ以外は chat 終了 (`Ctrl+D` 2 連続と同じ) |

> `:task next|prev|<letter>`/`:contest next|prev|<num|id>`/`:e` などの問題ナビゲーションコマンド (相対移動 + 直指定) は `atcoder start` の分割画面でのみ有効で、`test --interactive` 単体では未知コマンド (`E492`) として無視される ([027](./requirements/027-start-problem-navigation.md) / [031](./requirements/031-nav-direct-target.md))。

- **ビルダーの開閉**: `:case` で開く → 2 ペインを `Tab` で編集 → `Esc` で `:` 行へ → `:w` で保存 / `:q` で破棄。子プロセスには触れない (作成中も会話は裏で生きている)。
- **保存先**: `$XDG_CACHE_HOME/atcoder-tools/<contest>/<task>/tests-extra/NN.in|NN.out`。**`--refresh` で消えない** (公式サンプルの `tests/` とは別ディレクトリ)。空の `.out` でも保存でき、その場合は「実行できること自体の確認」用ケースになる。
- **ライブ検証**: expected を定義すると、以後の子 stdout を expected と**順序どおり**に突き合わせ、出力行の末尾に `✓` / `✗ expected …` を表示する。比較は `--tolerance` と同じ許容誤差。対話ジャッジ (入出力交互) では行対応が崩れるため `:set noverify` で切れる。

```
   2ms ← 9        ✓
   1ms ← 7        ✗ expected 8
```

保存した追加ケースは、次回以降 `atcoder test` / `atcoder start` のサンプル判定で**公式サンプルの後ろに連結**して走る。表示 id は公式が `01`…、追加が `x01`… (接頭辞 `x`)。`-c x01` で追加ケースだけを指定することもできる。`--refresh` は公式サンプルだけを取り直し、`tests-extra/` には触れない。

### 提出準備 (`--submit`)

`--submit` を付けると、サンプルが**全通過したとき**だけ続けて提出準備を行う (旧 `atcoder submit` を畳んだもの)。

1. 通常どおりサンプル判定。**全通過しなければ提出準備せず** `exit 1`。
2. 全通過なら、解答をクリップボードへコピーし、提出ページ (`/contests/<contest>/submit?taskScreenName=<task_id>`) をブラウザで開く。`--no-open` ならコピーして URL を表示するだけ。

```sh
atcoder test abc457 --task d --submit             # 緑ならコピー + ブラウザ起動
atcoder test abc457 --task d --submit --no-open   # コピー + URL 表示 (開かない)
```

> 実際の提出 (認証付き POST) は行わない (ブラウザで人間が提出)。AtCoder ログインは Cloudflare Turnstile 保護で programmatic 認証ができないため、認証付き実提出への格上げは見送り ([ADR 0006](./decisions/0006-fold-submit-into-test.md) / `todo.md`「K」)。`--submit` はサンプルモード専用で、`--in`/`--out`/`--interactive`・`--watch` とは併用不可 (`exit 2`)。

## 動作

1. `exercise/YYYY/MM/DD/<task>.py` の存在を確認 (無ければエラー)。
2. `$XDG_CACHE_HOME/atcoder-tools/<contest>/<task>/tests/` を確認:
   - 存在し `--refresh` も無ければそれを使う。
   - 無ければ AtCoder からサンプル入出力と Time Limit を取得して同ベースに保存。
3. 各サンプルケースに対して `<repo_root>/.venv/bin/python <task>.py < NN.in` を実行。
4. 標準出力を `NN.out` と比較し、結果をケースごとに表示。

## 判定種別

| ラベル | 意味 |
|---|---|
| `PASS` | 期待出力と一致 (末尾改行の差は無視) |
| `FAIL` | 期待出力と一致しない |
| `TLE` | 制限時間 (デフォルトは `meta.toml.time_limit_ms`、`--timeout` で上書き可) を超過 |
| `RE` | Python プロセスが非ゼロ終了 |

## 出力例

```
abc325_d  contest=abc325  time_limit=2000ms  tests=3

[01]  PASS  12 ms
[02]  FAIL  18 ms
       diff:
           2 │ - 1 2 3
           2 │ + 1 3 2
[03]  PASS  10 ms

Result: 2/3 PASS
```

`diff:` セクションは `delta` 風の unified diff:

- 一致行は省略 (差分のみ表示)
- 左から `<行番号> │ - / + <内容>`
- TTY (TrueColor) 端末では、行全体に subtle な背景色 (Mocha の red / green tint)、変化したトークンには bright な強調背景がのる
- パイプ / 非 TTY ではプレーンテキストにフォールバック (上記の見た目)

### exit code

| code | 意味 |
|---|---|
| `0` | 全ケース PASS |
| `1` | 実行できたが 1 ケース以上 FAIL/TLE/RE、または実行時エラー |
| `2` | 引数エラー (`--task` 未指定など) |

## ユースケース別の使い方

### 通常の演習チェック

```sh
# 短縮形 (ABC 系は contest + task で abcXXX 部分が重複するので便利)
go run ./cmd/atcoder test abc325 --task d

# 等価。フル ID で書いてもよい
go run ./cmd/atcoder test abc325 --task abc325_d
```

ADT のように contest ID と task ID が独立しているケースは、フル ID (`--task abc325_d` 等) で指定する。

### サンプルケースを最新化したい

問題ページが訂正されたり、自分で `tests/` を壊してしまったときに使う。

```sh
go run ./cmd/atcoder test abc325 --task abc325_d --refresh
```

### 解答コードを修正してリトライ

`tests/` はキャッシュされているので 2 回目以降のテストは高速。

```sh
# 解答を編集して保存後
go run ./cmd/atcoder test abc325 --task abc325_d
```

### 編集ループを回したい (watch モード)

`-w` / `--watch` を付けると常駐し、解答ファイルを保存するたびにテストを自動再実行する。エディタとターミナルを往復せず、保存だけで判定が回る。`Ctrl+C` で終了。

```sh
go run ./cmd/atcoder test abc325 --task abc325_d --watch
```

- 監視対象は**解答ファイル 1 つ**。保存 (mtime 変化) を検知するたびに画面をクリアして最新結果だけを描き直す。
- `--watch` は**端末 (TTY) が必要**。パイプやリダイレクト先では `exit 2` で拒否される (画面クリア前提のため)。
- `--refresh` と併用すると**初回のみ**再 fetch する (毎保存でネットワークを叩いて rate limit を踏むのを防ぐ)。`-c` / `-j` などの絞り込み・並列指定はそのまま各実行に効く。
- FAIL/RE/TLE でもループは止まらない。watch の終了コードは判定結果に依存せず、`Ctrl+C` での正常終了は `exit 0`。

### 解答コードにデバッグ出力を仕込みたい

`-d` 指定で子プロセスに `DEBUG=1` が渡る。Python 側で `os.environ.get("DEBUG")` を分岐すれば、デバッグ実行時のみログを出せる。出力行のうち先頭が `[DEBUG]` のものは比較対象から自動除外される。

```python
import os
DEBUG = bool(os.environ.get("DEBUG"))
def dprint(*args, **kwargs):
    if DEBUG:
        print("[DEBUG]", *args, **kwargs)

N = int(input())
dprint("N =", N)        # `-d` 時のみ [DEBUG] N = ... が出る
# ...
print(answer)
```

```sh
# 通常実行: DEBUG 未設定、デバッグ出力なし、判定通り
go run ./cmd/atcoder test abc325 --task d

# デバッグ実行: [DEBUG] 行を debug: セクションで確認しつつ判定もそのまま
go run ./cmd/atcoder test abc325 --task d -d

# 入力・出力もまとめて見たい
go run ./cmd/atcoder test abc325 --task d -d -v
```

### 制限時間を上書きしたい

問題ページの制限時間を超えても挙動を見たい / より厳しい制限で TLE をローカル検出したい、などのケース:

```sh
# AtCoder の値を無視して 5 秒で TLE 判定
go run ./cmd/atcoder test abc325 --task abc325_d --timeout 5s

# 自前の高速性検証で 200ms 以内に収まるか確認
go run ./cmd/atcoder test abc325 --task abc325_d --timeout 200ms
```

## トラブルシューティング

### `解答ファイルが見つかりません: exercise/YYYY/MM/DD/<task>.py`

- 当日の日付ディレクトリに `<task>.py` を作成しているか確認する。
- 日付ディレクトリが無い場合は `go run ./cmd/atcoder new` で作成する。
- 過去日の解答をテストしたいユースケースは現時点では未対応。

### `AtCoder から取得できませんでした (HTTP 4xx)`

- `<contest>` と `<task>` の綴りを確認する (例: `abc325` / `abc325_d`)。
- 一部の限定公開コンテストは未対応 (公開サンプルがある問題のみ対象)。

### サンプルの抽出に失敗

- AtCoder の HTML 構造が変わった可能性。`--refresh` でリトライしても直らなければ実装側で対応が必要。
- 一時しのぎとして `<task>/tests/NN.in` `NN.out` を手で書いてもテスト自体は通る。

### `python が見つかりません`

- `<repo_root>/.venv/bin/python` の存在を確認 (`poetry install`)。
- `.venv` を作りたくない環境では、`PATH` 上に `python` を通しておけばフォールバックされる。

### `TLE` が頻発する

- 解答自体の計算量を見直す。
- `meta.toml` の `time_limit_ms` が問題ページから誤って小さく取得された疑いがあれば、`--refresh` を試す、または手で書き換える。

## 設定ファイルで既定値を固定する

毎回付けているフラグの既定値は、ユーザ設定ファイルにまとめて書いておける。設定は **`$XDG_CONFIG_HOME/atcoder-daily-training/config.toml`** (未設定なら `~/.config/atcoder-daily-training/config.toml`) を読む。キャッシュ (`XDG_CACHE_HOME` 配下の `atcoder-tools/`) とは別軸。

```toml
# ~/.config/atcoder-daily-training/config.toml
[test]
side_by_side = true   # diff を常に side-by-side で表示 (-s 相当)
```

- 優先順位は **`flag > config > default`**。設定で `side_by_side = true` にしておけば `-s` 省略で side-by-side になり、その回だけ unified に戻したいときは `--side-by-side=false` を付ける。
- 設定ファイルが無いのは正常 (全項目デフォルト = 現行挙動)。**TOML の文法エラーがあるときだけ** `exit 2` で停止する。
- 未知のキー・セクションは無視される (前方/後方互換)。将来 `[test]` に他の既定値や `[run]` 等のセクションが増えても、古い・新しいバイナリ間で壊れない。

| キー | 型 | 既定 | 対応フラグ | 用途 |
|---|---|---|---|---|
| `test.side_by_side` | bool | `false` | `-s` / `--side-by-side` | FAIL 時の diff を side-by-side でレンダリングする既定値 |

### `atcoder config` で設定をいじる

`config.toml` を手で開かなくても、`atcoder config` サブコマンドで閲覧・編集できる。

```sh
atcoder config show                        # 既知キーと現在値を一覧
atcoder config get test.side_by_side       # 1 キーの現在値を出力
atcoder config set test.side_by_side true  # 書き込み (config.toml を作成/更新)
atcoder config path                        # config.toml の絶対パスを出力
```

```
$ atcoder config show
test.side_by_side = false
$ atcoder config set test.side_by_side true
set test.side_by_side = true  (/Users/you/.config/atcoder-daily-training/config.toml)
$ atcoder config get test.side_by_side
true
```

- キーは **`<section>.<field>`** のドット区切り (例 `test.side_by_side`)。指定できるキーは上表のとおり (`config show` でも一覧できる)。
- `set` は `config.toml` が無ければ親ディレクトリごと作成し、**既存の他キー・未知キー・他セクションは保全**して該当キーだけ更新する。
- **未知キー・型に合わない値・未知サブコマンド・引数不足は `exit 2`**、`config.toml` の書き込み失敗は `exit 1`。
- `set` した値は次回以降の `atcoder test` が読む (優先順位 `flag > config > default` は上記のまま)。

## 制約事項 (現時点)

- 対応言語は Python のみ。
- 対象ディレクトリは `exercise/YYYY/MM/DD/` 配下のみ (`abc/`, `arc/`, `adt/`, `dp/` などは未対応)。
- 解答ファイルは当日のディレクトリにあるものに限る。
- 認証が必要な限定公開コンテストは未対応。

## 関連

- 要件定義: [001-exercise-test.md](./requirements/001-exercise-test.md)
- アーキテクチャ: [atcoder-test-architecture.md](./atcoder-test-architecture.md)
- テスト戦略: [atcoder-test-testing.md](./atcoder-test-testing.md)
- test/run 統一の経緯: [013-unify-test-run.md](./requirements/013-unify-test-run.md) / [ADR 0005](./decisions/0005-unify-test-run-into-test.md)
- コミットコマンド: [atcoder-commit-usage.md](./atcoder-commit-usage.md)
- ツール本体: [`cmd/atcoder/main.go`](../../cmd/atcoder/main.go)
