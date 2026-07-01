# インタラクティブモードの入出力ケース作成 + ライブ検証 要件定義

## 概要

インタラクティブ chat の中から、**vim 風コマンドモード**を起点に「追加の入出力ケース」を 1 つ作成・保存できるようにする。入力 (`.in`) は今のセッションで打った行を自動で前埋めし、期待出力 (`.out`) は手入力で定義する。期待出力を定義すると、ファイル保存とは独立に **インタラクティブモード中でも子の stdout をライブ検証** (行ごとに一致/不一致を inline 表示) できる。保存したケースは `--refresh` で消えない専用ディレクトリ (`tests-extra/`) に置かれ、`atcoder test` / `atcoder start` の判定ループに公式サンプルと並んで載る。これは ABC ロードマップ **F.「WA / penalty 後のワークフロー (ユーザ追加ケース)」** を畳む設計でもある。

## 背景・目的

- 公式サンプルは PASS でも提出すると WA、というとき、自分で edge case を書いて再テストしたい。今の cache (`$XDG_CACHE_HOME/atcoder-tools/<contest>/<task>/tests/`) は `--refresh` で上書きされるため、自作ケースを置いても消える (F の課題)。
- インタラクティブ chat ([019](019-interactive-output-timing.md)〜[022](022-interactive-unify-quit-keys.md)) は、子に手で入力を流して挙動を確かめる場として既に機能している。**そこで見つけた再現入力をその場でケース化**できれば、「気づく → 試す → 固定する」が 1 画面で完結する。chat は打った入力 (`kindIn`) と子の出力 (`kindOut`) を既に全部保持しているので、セッションからの取り込みは自然。
- 入力を流すだけだと「出力が合っているか」は目視に頼る。期待出力を一度定義すれば、以後のやり取りを**ライブ検証**して PASS/不一致を即座に示せる (ファイルに残すかは別問題)。

## スコープ

| | 当面のスコープ (この要件) | 将来の拡張余地 (別要件) |
|---|---|---|
| 起動 | chat 内の vim 風コマンドモード (ex-command line `:…`) | normal-mode 風の単一キー操作 (`j`/`k` でスクロール等) |
| 入力 `.in` | セッションの送信入力 (`kindIn` 行) を改行区切りで前埋め・編集可 | 範囲選択して一部行だけ取り込む |
| 期待出力 `.out` | 手入力 (複数行)。空のまま保存も可 (入力のみケース) | 観測した stdout からの前埋め取り込み (取り込みボタン) |
| ライブ検証 | 期待出力を順序どおり子 stdout と突き合わせ、行ごとに一致/不一致を inline 表示 | reactive (対話ジャッジ) 用のプロトコル検証 |
| 保存先 | `tests-extra/NN.in|NN.out` (cache 配下、`--refresh` 不可侵) | repo 内保存オプション (`abc/<contest>/<letter>.tests/`) |
| 消費 | `atcoder test` / `start` が公式の後に `tests-extra` を判定。表示 id は `x01` 形式 | ケースの編集 (`:e`) / 削除 (`:d`) コマンド |

**境界:**

- **F (ユーザ追加ケース)** はこの要件が実装に落とす。`tests-extra/` という保存場所・`--refresh` 非破壊・判定ループ統合は F の「決めること」をここで確定させる。
- **G (タイマー / コンテスト状態 TUI)** とは独立。ケース作成は contest 状態を参照しない。
- 解答ファイル (ユーザの提出コード) には一切触れない。作成・保存対象は cache 配下の `tests-extra/` のみ。

## ディレクトリ構造 / スキーマ

```
$XDG_CACHE_HOME/atcoder-tools/<contest>/<task>/
  meta.toml            # 既存。変更なし
  tests/               # 既存。公式サンプル。--refresh で上書きされる
    01.in  01.out
    ...
  tests-extra/         # 新規。ユーザ追加ケース。--refresh で消さない
    01.in  01.out      # 独自に 01 始まりの連番 (公式とは別系統)
    02.in  02.out
    ...
```

| 項目 | 規約 |
|---|---|
| ファイル名 | `tests-extra/NN.in` / `NN.out` (`%02d`, 01 始まり)。公式 `tests/` と同じ命名だが**別ディレクトリ**なので衝突しない |
| 連番採番 | 保存時に `tests-extra/` 内の既存最大番号 + 1 を採番 (`Save` が決定)。名前を明示指定すれば任意名も可 |
| 表示 id | 判定・レポートでは公式 = `01`、追加 = `x01` (接頭辞 `x` = extra)。`x` は ASCII で数字の後にソートされ、公式の後に並ぶ |
| `.out` の扱い | 空ファイルも許容。空 `.out` のケースは「出力検証なし (実行できること自体の確認)」として走らせる (judge は expected 空なら出力の有無を問わない) |

## CLI / TUI 仕様

新しいサブコマンドやフラグは**増やさない**。すべて既存のインタラクティブ chat (`atcoder test --interactive …` / `atcoder start` の `i`) の内側で完結する。

### モード遷移 (vim 風)

chat は 2 つの入力モードを持つ。

| モード | 説明 | 抜け方 |
|---|---|---|
| **insert** (既定) | 現状の chat。textinput にフォーカスし、Enter で子に送信 | `Esc` で command へ |
| **command** (ex-command line) | 入力欄が `:` プロンプトに変わり、コマンドを 1 行打って Enter で実行 | `Enter` (実行して insert へ) / `Esc` (キャンセルして insert へ) |

> **トリガーの決定 (Ctrl+: は使わない):** 当初要望は「`Ctrl+:` でコマンドモード」だったが、bubbletea v1.3.10 は `Ctrl+:` を固有のキーコードとして受け取れない (命名済み Ctrl 組合せは Ctrl+英字 と `Ctrl+@ [ \ ] ^ _ backtick` のみ。`:` は素の `KeyRunes` として届く)。これは [022](022-interactive-unify-quit-keys.md) で確認した「raw モードの端末キーの罠」と同種。そこで vim の「insert を抜けて ex-command を開く」流儀に忠実に、**`Esc` で command モードへ → `:` プロンプト**とする。`Esc` は `KeyEsc` として確実に届き、現状 chat 内で未使用。詳細と却下案は [ADR 0007](../decisions/0007-interactive-command-mode-trigger.md)。

### コマンド一覧

| コマンド (別名) | 動作 | MVP |
|---|---|---|
| `:case` (`:c`) | **ケースビルダー画面**を開く。`.in` を現セッションの送信入力で前埋めし、`.out` 入力ペインへ | ✅ |
| `:w [name]` | ビルダー内で現在の `.in` / `.out` を `tests-extra/` に保存 (`name` 省略時は連番)。保存後 chat に戻る | ✅ |
| `:set verify` / `:set noverify` | ライブ検証の on/off。`:case` で `.out` を定義すると自動 on | ✅ |
| `:q` | chat を終了 (`Ctrl+D` と同じ。子を kill して quit)。vim 慣れ向けの別名 | 任意 |
| `Esc` | command モードのキャンセル (insert へ) / ビルダーを閉じる | ✅ |

未知コマンドは command line にエラー (`E492: unknown command`) を 1 行出して insert に戻る (副作用なし)。

### ケースビルダー画面

`:case` で開くモーダル (chat の上に重ねる。**子プロセスは起動も kill もしない** — 既存セッションは生かしたまま)。

```
┌─ new case ───────────────────────────────── tests-extra/x03 ─┐
│ input (.in)        ← セッションの送信入力で前埋め・編集可     │
│   5 3                                                         │
│   1 2 3 4 5                                                   │
│ expected (.out)    ← 手入力 (空でも可)                        │
│   9                                                           │
│                                                               │
│ :w で保存 / Esc で取消  (Tab でペイン切替)                    │
└───────────────────────────────────────────────────────────────┘
```

- 2 ペイン (input / expected) を `Tab` で行き来する。複数行編集のため bubbles の `textarea` を新規導入する。
- `:w [name]` で保存。`.in` は input ペインの全文、`.out` は expected ペインの全文。
- 保存に成功したら chat に戻り、info 行 `(saved tests-extra/x03)` を出す。`Esc` で破棄して chat に戻る。

### ライブ検証 (インタラクティブ中の出力検証)

- expected が定義されている (ビルダーで入力した or `:set verify`) あいだ、子の stdout 行 (`kindOut`) を expected の行と**順序どおり**に突き合わせる。
- 各 stdout 行の inline インジケーターで一致/不一致を示す: 一致 `✓` (緑) / 不一致 `✗` (赤、期待値を併記) / expected 行が尽きたら検証対象外 (従来表示)。
- 比較は `atcoder test` の judge と同じ許容誤差 (`--tolerance`) ロジックを再利用する (浮動小数の問題で揃える)。
- **対話ジャッジ (reactive) の caveat:** 入力と出力が交互に来る問題では「stdout の i 行目 = expected の i 行目」という対応が崩れる。ライブ検証はあくまで**バッチ的に stdout を順に突き合わせる**セマンティクスに限定し、reactive 向けのプロトコル検証は将来要件 (スコープ表参照) とする。検証が無意味な問題では `:set noverify` で切る。

### 出力イメージ (chat 内のライブ検証)

```
   2ms ← 9        ✓
   1ms ← 7        ✗ expected 8
```

## 動作仕様

| 観点 | 仕様 |
|---|---|
| 冪等性 (保存) | `:w` は常に新規ケースを 1 つ追加する (上書きしない)。連番は `tests-extra/` の現状から採番。同名指定時のみ上書き確認を出す (MVP は上書き拒否 = エラー) |
| `--refresh` 非破壊 | `--refresh` は `tests/` (公式) のみ再取得・上書きする。`tests-extra/` は読まないし消さない。`ensureTests` の対象に `tests-extra` を含めない |
| セッション取り込み | `.in` 前埋めは現セッションの `kindIn` 行のみ (auto-restart / watch-reload で区切られた過去セッションは含めない)。送信していない (Enter 前の) 入力は対象外 |
| ライブ検証の独立性 | 検証はメモリ上の expected で動く。**ファイル保存は必須でない** (`:case` で expected だけ入れて `Esc` でも検証は有効化できる) |
| 既存ワークフロー共存 | command モード・ビルダーは insert モードの既存挙動 (Enter 送信・履歴 Up/Down・出力タイミング・auto-restart・watch-reload) を一切変えない。`Esc` を押さない限り全く同じ |
| start との入れ子整合 | `start` → `i` → chat → `Esc`/`:case` → ビルダー → `:w`/`Esc` → chat → `Ctrl+D` (or `:q`) → start watch、という入れ子を保つ。`Ctrl+C` は chat 内でプログラム中断・再起動 ([025](025-interactive-ctrl-c-interrupt.md)) で start watch には戻らない。ビルダーは chat 内モーダルで完結し、子も start ループも触らない。auto-restart 中でもビルダーは開ける |
| 消費 (test/start) | `atcoder test` / `start` は公式 `tests/` の後に `tests-extra/` を連結して判定する。並列実行・サマリ集計・exit code は既存どおり (全 PASS = 0、いずれか FAIL/RE/TLE = 1)。表示 id で公式 (`01`) と追加 (`x01`) を区別 |

## 影響範囲

| ファイル / パッケージ | 変更内容 |
|---|---|
| `internal/ui/chat.go` | モード状態 (`insert`/`command`) を `chatModel` に追加。`Esc` で command へ、`:` プロンプト描画とコマンドパーサ、ビルダー画面 (textarea 2 ペイン)、ライブ検証 (stdout 行と expected の突き合わせ + inline インジケーター)。`Ctrl+D`=終了 / `Ctrl+C`=中断・再起動 ([025](025-interactive-ctrl-c-interrupt.md)) は不変 |
| `internal/ui/` (新規スタイル) | command line / ビルダー枠 / 検証インジケーター (`✓`/`✗`) のスタイル。`textarea` 依存を追加 (`github.com/charmbracelet/bubbles/textarea`) |
| `internal/extracase/` (新規) | `tests-extra/` の解決・保存・列挙を担う小パッケージ。ui (保存) と testexec (列挙) の両方から使う |
| `internal/testexec/test.go` | `listCases` を「`tests/` + `tests-extra/`」の 2 系統列挙に拡張。表示 id 付与 (`x` 接頭辞)。`ensureTests`/`--refresh` は `tests/` のみ対象のまま (tests-extra 不可侵) |
| `cmd/atcoder/` | 変更なし (新フラグ・新サブコマンドなし)。chat 起動経路 (`test --interactive` / `start`) はそのまま |

### 新規 `internal/extracase/` パッケージの責務 (API 素描)

```go
// Package extracase は contest/task のユーザ追加ケース (tests-extra/) の
// 場所解決・保存・列挙を担う。--refresh で消える tests/ とは別系統として扱う。
package extracase

// Dir は taskDir (cache 配下の <contest>/<task>) に対する tests-extra のパスを返す。
func Dir(taskDir string) string

// Save は input/expected を tests-extra/<name>.in|.out に書き出す。
// name が空なら既存最大番号 + 1 の %02d を採番し、付与した名前を返す。
// 既存 name への上書きは error (冪等性のため MVP では拒否)。
func Save(taskDir, name string, input, expected []byte) (caseName string, err error)

// List は tests-extra のケース名 (NN) を昇順で返す。ディレクトリが無ければ
// 空スライスと nil を返す (追加ケースが無いのは正常)。
func List(taskDir string) ([]string, error)
```

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| 未知コマンド (`:foo`) | command line に `E492: unknown command` を 1 行表示し insert へ。副作用なし・exit しない |
| `:w` で既存名を指定し衝突 | 保存せずエラー行を出す (MVP は上書き拒否)。ビルダーは開いたまま |
| `tests-extra/` 作成失敗 (権限等) | ビルダーにエラー行を出し保存中止。chat は継続 (落とさない) |
| ビルダーを `Esc` で閉じた | 破棄。ファイルは作らない。検証用 expected も破棄 (`:set verify` 済みなら検証は維持) |
| 消費時 `tests-extra/` が壊れている (`.in` だけ等) | その追加ケースを `RE`/`FAIL` 相当で 1 件報告 (実行時失敗 = exit 1)。公式ケースの判定は妨げない |
| 引数なしのコマンド誤用 | command line にメッセージを出して insert へ (chat の exit code には影響しない。CLI 全体の引数誤り = 2 とは別レイヤ) |

## 非機能要件

- **既存非破壊:** `Esc` を押さない限り chat の挙動は完全に従来どおり ([019](019-interactive-output-timing.md)〜[022](022-interactive-unify-quit-keys.md) の仕様を変えない)。解答ファイルには触れない。
- **`--refresh` 安全性:** `tests-extra/` は fetch/refresh の対象外。確立済みの「`--refresh` は cache の公式サンプルのみ」を保つ。
- **前方互換:** `tests-extra/` は独立ディレクトリなので、後から G (本番モード) や別 fetch 経路が来ても `tests/` の取得ロジックと干渉しない。表示 id の `x` 接頭辞は将来の別系統 (例 hack ケース) を増やす余地を残す。
- **exit code 規約:** 追加ケースを混ぜても全 PASS = 0 / いずれか失敗 = 1 / 引数・フラグ誤り = 2 を維持。
- **端末キー堅牢性:** トリガーは確実に届く `Esc` に倒す ([ADR 0007](../decisions/0007-interactive-command-mode-trigger.md))。raw モードで受信不能なキー (Ctrl+:) に依存しない。

## 将来の拡張ポイント

- `:e <id>` で既存追加ケースを編集、`:d <id>` で削除。
- 観測した stdout からの expected 前埋め (「直前のセッション出力を期待値として取り込む」)。
- reactive (対話ジャッジ) 用のプロトコル検証 (入出力交互の対応付け)。
- repo 内保存オプション (`abc/<contest>/<letter>.tests/`) — git 履歴に残したいケース向け (F の第 2 候補)。
- normal-mode 風の単一キー操作 (スクロール `j`/`k`、ヤンク等)。

## 用語

- `contest_id` = `abc457` / `contest_num` = `457` / `task_id` = `abc457_d` / `letter` = `d` (既存要件に準拠)。
- **公式ケース** = AtCoder から fetch して `tests/` に置くサンプル (`01`…)。
- **追加ケース** = ユーザがビルダーで作り `tests-extra/` に置くケース (表示 id `x01`…)。
- **insert / command モード** = chat の入力モード。command は vim の ex-command line に相当。

## 関連ドキュメント

- ロードマップ: [`abc-todo.md`](../abc-todo.md) の **F. WA / penalty 後のワークフロー** (この要件が実装に落とす) / `todo.md`
- 決定記録: [ADR 0007 — インタラクティブ command モードのトリガー](../decisions/0007-interactive-command-mode-trigger.md)
- インタラクティブ chat の既存仕様: [019](019-interactive-output-timing.md) / [020](020-interactive-auto-restart-flag.md) / [021](021-interactive-ctrl-d-quit.md) / [022](022-interactive-unify-quit-keys.md)
- start コマンド: [018](018-start-command.md) / [054-start-key-actions](054-start-key-actions.md) / [023-start-split-screen](023-start-split-screen.md)
- 利用手引: `docs/tools/usage/test.md` (実装時に command モード / ビルダー / ライブ検証を追記)
