# chat コマンドモードの Tab 補完 要件定義

## 概要

chat (`test --interactive` 単体 / `atcoder start` 分割画面の下ペイン) の vim 風コマンドモード ([024](024-interactive-case-builder.md) / [ADR 0007](../decisions/0007-interactive-command-mode-trigger.md)) の `:` 行で、**`Tab` を押すとコマンド名・サブトークンを補完**できるようにする。`:ca`+Tab → `:case`、`:set v`+Tab → `:set verify`、`:task n`+Tab → `:task next` のように、最長共通プレフィックスまで補完し、候補が複数なら候補一覧を 1 行表示する (bash 風)。新しいコマンドや実行経路は増やさず、既存の `:` 行 (`cmdInput`) に補完キーを 1 つ足すだけの薄い追加とする。

## 背景・目的

- コマンドモードのコマンド (`:case`/`:w`/`:set`/`:q`/`:task`/`:contest`/`:e`) と、その引数 (`:set verify|noverify`、`:task`/`:contest` の `next|prev`) は数も語形も覚えにくく、毎回フルで打つかドキュメントを見に行く必要がある。`Tab` で補完できれば、コマンド体系を覚えていなくても候補から手が動く。
- start のナビゲーション ([027](027-start-problem-navigation.md)) で `:task next|prev` / `:contest next|prev` という 2 トークン文法が入り、打鍵数が増えた。補完はこの文法と特に相性がよい。
- コマンドモードは既に `Esc` → `:` で入る確実な入力経路 ([ADR 0007])。`Tab` はそのモード内のキーで、raw モードでも確実に受信できる (`Alt`/`Shift`+キーのような取りこぼしの罠がない)。builder モードの `Tab` (ペイン切替) とはモードが別なので衝突しない。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| トリガ | コマンドモード (`:` 行) での `Tab` のみ | `Shift+Tab` で逆方向循環 |
| 補完位置 | 第 1 トークン (コマンド名) / 第 2 トークン (既知サブトークン) | 第 3 トークン以降 |
| コマンド名候補 | `case`/`w`/`set`/`q`/`debug`/`cheat` (常時) + `task`/`contest`/`e` (NavEnabled 時) | ユーザ定義エイリアス |
| サブトークン候補 | `:set` → `verify`/`noverify`/`debug`/`nodebug`、`:task`/`:contest` → `next`/`prev` | — |
| `:e <spec>` の候補 | **対象外** (問題知識が要るため。第 1 トークン `e` の補完のみ) | letter 一覧・隣接 contest・履歴からの候補 ([027] 将来拡張と連携) |
| 候補の出し方 | 最長共通プレフィックスまで補完 + 複数なら候補一覧を 1 行表示 (bash 風) | 循環 (menu-complete)・候補のハイライト選択 |
| 表示 | command モードの `:` 行の直下に dim な候補行 | 補完候補のグリッド整形 |

### 境界 (他機能との分担)

- 補完ロジックは **`internal/ui` の純粋関数** `completeCommandLine(line, navEnabled)` に閉じる。子プロセス・stdout・解答ファイルには一切触れない (`:` 行の編集のみ)。
- コマンドの **語彙** (受理されるコマンド名・別名・サブトークン) の正は `parseCommand` ([024]) と `navRequestFor` ([027]) のままで、補完はそれと整合する**候補表**を持つ。候補表とパーサが食い違わないよう、補完候補は「正規形 (canonical) のコマンド名」を返す (別名 `:c`/`:n` 等は候補に出さないが、入力中のプレフィックスとしては受理される)。
- NavEnabled ([027]) による出し分けに従う: `task`/`contest`/`e` は start 分割画面 (NavEnabled=true) でのみ候補に出す。`test --interactive` 単体では出さない (打っても `E492` になるコマンドを勧めない)。
- 実行 (`Enter`)・キャンセル (`Esc`)・既存コマンドの挙動は不変。`Tab` は補完だけを行い、モード遷移や実行はしない。

## CLI / TUI 仕様

新しいサブコマンド・フラグは増やさない。すべてコマンドモード内の `Tab` で完結する。

### 補完の対象と候補

| 位置 | 入力状態 | 候補集合 |
|---|---|---|
| 第 1 トークン | `:` 行が空、または 1 語目を入力中 (末尾が空白でない) | `case`/`cheat`/`debug`/`q`/`set`/`w` (常時) + `contest`/`e`/`task` (NavEnabled 時)。アルファベット順 |
| 第 2 トークン | 1 語目 + 空白の後、または 2 語目を入力中 | 1 語目が `set` → `debug`/`nodebug`/`noverify`/`verify`、`task`/`contest` → `next`/`prev`。それ以外 → 候補なし |
| 第 3 トークン以降 | 2 語目 + 空白の後 | 候補なし (無反応) |

### 補完の挙動 (`Tab` 1 回)

1. 現在の `:` 行を純粋関数 `completeCommandLine(line, navEnabled)` に渡し、`(replacement, candidates)` を得る。
2. 現トークンのプレフィックスに前方一致する候補を絞り込む。
   - **0 件** → 行は変えない・候補行も出さない (無反応)。
   - **1 件** → 現トークンをその候補で**確定**。確定したコマンドが後続トークンを取る (`set`/`task`/`contest`/`e`) なら末尾に空白を 1 つ足す (続けて打てる)。候補行は消す。
   - **複数件** → 現トークンを候補群の**最長共通プレフィックス**まで伸ばし、候補一覧を候補行に表示する。
3. 行が変わったら `cmdInput` に反映 (カーソルは行末へ)。`Tab` 以外のキーを打つ・実行・キャンセルすると候補行は消える。

### 画面イメージ

```
:ca          ← Tab
  ↓ 1 件 (case) に確定
:case

:c           ← Tab  (start 分割画面 = NavEnabled)
  ↓ 複数 (case, contest) → 共通プレフィックス "c" のまま候補表示
:c
  case  contest          ← 候補行 (dim)

:set v       ← Tab
  ↓ 1 件 (verify) に確定
:set verify

:task        ← Tab (空白の後)
  ↓ next / prev を候補表示
:task
  next  prev             ← 候補行 (dim)
```

## 動作仕様

| 状況 | 挙動 |
|---|---|
| `:` 空 + Tab | コマンド名の全候補 (NavEnabled で出し分け) を候補行に表示 (共通プレフィックスが無ければ行は空のまま) |
| 一意に決まるプレフィックス + Tab | フル補完。後続トークンを取るコマンドは末尾に空白を付与 |
| 複数一致 + Tab | 最長共通プレフィックスまで補完し候補一覧を表示 |
| 一致 0 + Tab | 無反応 (行も候補行も変えない) |
| `:set `/`:task `/`:contest ` + Tab | そのコマンドのサブトークンを候補表示 |
| 後続トークンを取らないコマンド (`case`/`q`/`w`) の後 + Tab | 候補なし (無反応) |
| `test --interactive` 単体で Tab | `task`/`contest`/`e` は候補に出さない (NavEnabled=false)。`case`/`w`/`set`/`q` は出る |
| builder モードの Tab | 従来どおりペイン切替 (本要件の対象外。command モードとは別) |
| Enter / Esc | 従来どおり実行 / キャンセル。候補行はクリア |

- **既存非破壊**: `Tab` を押さない限りコマンドモードの挙動は従来どおり ([024]/[027])。補完は `:` 行の文字列を編集するだけで、コマンドの実行経路・パーサ・子プロセスには影響しない。
- **stdout 非汚染**: 候補行は TUI 内 (command モードの `:` 行直下) にのみ描画し、子プロセスや stdout には書かない。
- **語彙の単一情報源との整合**: 補完候補は canonical 名のみを返し、`parseCommand`/`navRequestFor` が受理する語と矛盾しないようにする。

## 影響範囲

| ファイル / パッケージ | 変更内容 |
|---|---|
| `internal/ui/command_complete.go` (新規) | 純粋関数 `completeCommandLine(line string, navEnabled bool) (replacement string, candidates []string)` と候補表 (`commandNames(navEnabled)`・サブトークン map・後続トークンを取るコマンド集合)、補助 (`filterByPrefix`/`longestCommonPrefix`) を置く |
| `internal/ui/chat_casebuilder.go` | `updateCommand` に `tea.KeyTab` 分岐を追加 (補完を適用し候補を `m.cmdCandidates` に格納)。default (タイプ) で候補をクリア。command モードのレンダリングを `renderCommandLine()` に集約し候補行を足す |
| `internal/ui/chat.go` | `chatModel` に `cmdCandidates []string` を追加。command モードの View (`m.cmdInput.View()`) を `m.renderCommandLine()` に差し替え |
| `internal/ui/command_complete_test.go` (新規) | `completeCommandLine` のテーブルテスト (第 1/第 2 トークン・一意/複数/0 件・NavEnabled 出し分け・末尾空白付与・共通プレフィックス) |
| `docs/tools/atcoder-test-usage.md` / `atcoder-start-usage.md` | コマンドモード節に「`Tab` で補完」を追記 |
| `docs/tools/todo.md` | 該当項目に補完の節を足し、本要件へ相互リンク |

### API 素描

```go
// internal/ui — コマンドモードの Tab 補完 (純粋関数。子プロセス・stdout に触れない)。

// completeCommandLine は command モードの `:` 行 line を Tab 補完する純粋関数。
// navEnabled は task/contest/e (start 分割画面限定コマンド) を候補に含めるか。
//   - replacement: 補完後の行 (変化が無ければ line と同じ)。
//   - candidates : 複数一致のとき表示する候補一覧 (1 件確定・0 件なら nil)。
func completeCommandLine(line string, navEnabled bool) (replacement string, candidates []string)
```

- **層境界**: 純粋関数は `internal/ui` に閉じ、`cmd/atcoder` へは波及しない (NavEnabled は既存の `ChatHeader.NavEnabled` から取る)。

## エラーハンドリング

補完はコマンドモード内の編集補助なので、失敗してもプログラムは落とさない・exit code は変えない。

| 状況 | 動作 | exit |
|---|---|---|
| 一致候補 0 件で Tab | 無反応 (行・候補行を変えない) | (継続) |
| 補完後に不正なコマンドが残る | 補完は文字列編集のみ。`Enter` 時に従来どおり `E492` 等で処理 | (継続) |
| 非 TTY | コマンドモード自体が TTY 前提。`fixtures/run.sh` は非 TTY = exit 2 のみ assert で不変 | 2 |

## 非機能要件

- **薄い追加**: 新コマンド・新実行経路を増やさない。`:` 行の文字列補完だけを足す。
- **既存非破壊・前方互換**: `Tab` を押さなければ [024]/[027] の挙動は不変。`cmdCandidates` 既定 nil で表示も増えない。候補表は canonical 名のみで `parseCommand`/`navRequestFor` と整合。
- **決定的にテストできる純粋関数に**: 補完ロジック (`completeCommandLine` と補助) をユニットテストで固定する。`Tab` 駆動・候補行の描画は TTY 必須で手動確認 ([027] と同方針)。
- **端末キー堅牢性**: トリガは受信確実な `Tab` ([ADR 0007] の罠を避ける)。

## 将来の拡張ポイント

- **`:e` の候補**: letter 一覧 (`a`..`現在の上限`)・隣接 contest・移動履歴を候補に ([027] の「`:e` の補完・履歴」拡張と連携)。
- **循環補完**: `Tab` 連打で候補を順に巡回 (menu-complete)、`Shift+Tab` で逆順。
- **候補のグリッド整形**: 候補が多いときの複数行・幅揃え表示。

## 用語

- **コマンドモード**: `Esc` → `:` で入る 1 行コマンド入力モード ([024])。
- **補完 (completion)**: `:` 行の現トークンを候補の最長共通プレフィックス/一意候補まで自動で埋める操作。
- **候補行**: 複数候補があるとき `:` 行直下に出す dim な候補一覧。
- `contest_id` = `abc457` / `task_id` = `abc457_d` / `letter` = `d` (既存要件に準拠)。

## 関連ドキュメント

- `docs/tools/requirements/024-interactive-case-builder.md` (vim 風コマンドモードの土台・`parseCommand`)
- `docs/tools/requirements/027-start-problem-navigation.md` (`:task`/`:contest`/`:e` と `NavEnabled`)
- `docs/tools/decisions/0007-interactive-command-mode-trigger.md` (`Esc` トリガ・受信不能キーの罠)
- `docs/tools/atcoder-test-usage.md` / `atcoder-start-usage.md` (利用手引・実装時に Tab 補完を追記)
