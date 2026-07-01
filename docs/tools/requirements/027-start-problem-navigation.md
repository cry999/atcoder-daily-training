# `atcoder start` 問題ナビゲーション (letter / number の next・prev 移動) 要件定義

> **追記 ([032](032-nav-direct-target.md)):** `:contest` / `:task` に **直指定 (絶対ジャンプ)** を足した。`next`/`prev` 以外の非空トークンを `:task <letter>` (現コンテストの記号) / `:contest <num|id>` (コンテスト直指定・letter 保持) として解決する (`NavLetterExplicit` / `NavContestExplicit`)。相対移動と `:e` は不変。

## 概要

`atcoder start` の分割画面に居たまま、**現在の問題から隣の問題へ移動**できるようにする。下ペイン chat の **vim 風コマンドモード** ([024](024-interactive-case-builder.md) / [ADR 0007](../decisions/0007-interactive-command-mode-trigger.md)) を拡張し、

- `:task next` / `:task prev` (別名 `:task n` / `:task p`) … **問題記号 (letter)** を次/前へ (`abc457_d` ↔ `abc457_e` / `abc457_c`)
- `:contest next` / `:contest prev` (別名 `:contest n` / `:contest p`) … **コンテスト番号 (contest_num)** を次/前へ (`abc457` ↔ `abc458` / `abc456`、letter は保持)
- `:e <spec>` … 任意の問題へジャンプ (`:e f` / `:e abc500_d`)

を打つと、移動先の問題に **着手** ([018](018-start-command.md) と同じ: 解答ファイルが無ければ空ファイルを作成) し、分割画面の watch ペイン・chat ペインを**新しい問題で再ターゲット**する。新しい fetch / judge ロジックは増やさず、既存の ID 操作 (`internal/layout`)・`ensureSolutionFile`・`ui.RunStartSplit` を束ねる薄い orchestration とする。

## 背景・目的

- 練習の自然な動線は「同じコンテストを `a → b → c …` と順に解く」か「同じ letter を別コンテストで埋める (`abc457_d → abc458_d → …`)」だが、今はそのたびに **一度 `Ctrl+C` で start を抜け、`atcoder start abc458 --task d` を打ち直す**必要がある。分割画面に居たまま隣の問題へ移れれば、この往復が消える。
- letter 軸 = 同一コンテスト内の次の問題、number 軸 = 同じ letter の隣コンテスト、という 2 方向は AtCoder の問題 ID (`contest_num` + `letter`) の 2 成分そのもので、移動の意味が一意に定まる。
- start は既に分割画面 (bubbletea) で、コマンドモード ([024]) という「`Esc` → `:` で 1 行コマンドを打つ」入力経路を持っている。ナビゲーションはここに乗せるのが最も自然で、受信確実なキー (`Esc`) だけで完結する ([ADR 0007] の教訓に沿う)。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 対象 | `atcoder start` の分割画面 (TTY) の chat コマンドモードのみ | `test --interactive` 単体 (start でない chat) は対象外 |
| letter 移動 | `:task next` / `:task prev` で単一文字 letter を ±1 (`a`..`z`) | 複数文字 letter (`ex` 等) の移動 |
| number 移動 | `:contest next` / `:contest prev` で `<英字接頭辞><数字>` 形式の contest 番号を ±1 | 連続スキップ (`:contest next 3`) |
| 任意ジャンプ | `:e <letter>` / `:e <contest>_<letter>` | `:e` の補完候補・履歴 |
| 移動時の着手 | 解答ファイルが無ければ**空ファイル**を作成 (start と同じ。既存は温存) | テンプレート流し込み (ロードマップ H) |
| 再ターゲット | watch ペインのサンプル判定・chat ペインの子プロセスを新問題で作り直す | 「次の**未着手** letter へ飛ぶ」スキップ移動 |
| レイアウト | 現在の `--layout` 選択を保持し、新 contest_id で再解決 (`auto` は再判定) | — |
| 言語 | Python (既存 runner のまま) | 他言語 runner |

### 境界 (他機能との分担)

- ID の増減 (`d → e` / `abc457 → abc458`) は **`internal/layout`** の純粋関数に置く。`ContestNum` / `TaskID` / `Letter` ([002] / 018) と同じ「layout に依存しない ID 操作」の仲間として追加する。
- 移動先への**着手** (親 dir 作成 + 空ファイル生成、既存温存) は `start` の `ensureSolutionFile` ([018]) をそのまま再利用する。独自のファイル生成ロジックは増やさない。
- サンプル fetch・判定は **`testexec`** ([001])。移動後の watch ペインは新 contest/task に束ねた `SampleRunner` を回すだけで、初回判定時に lazy fetch される (cache)。`--refresh` 相当の再取得はしない。
- コマンドモードの土台 (`Esc` → `:` プロンプト・パーサ・未知コマンドの `E492`) は [024] / [ADR 0007]。本要件はそこに**ナビゲーションコマンドを足す**だけで、既存コマンド (`:case`/`:w`/`:set`/`:q`) は不変。
- 再ターゲットの状態遷移は **親 `startSplitModel`** ([023]) が握る。chat (下ペイン) はコマンドを**パースして親へ通知**するだけで、layout 解決・ファイル生成・子の作り直しはしない (`internal/ui` は `cmd/atcoder` を import できない層境界を保つ)。

## ID 操作スキーマ

移動は現在の `(contest_id, task)` を起点に、純粋関数で隣の ID を計算する。

| 関数 (新規 `internal/layout`) | 入力 → 出力 | 境界・エラー |
|---|---|---|
| `ShiftLetter(letter, delta)` | `("d", +1) → "e"` / `("d", -1) → "c"` | `a` 未満は `error` (下限)。単一 `a`..`z` のみ。複数文字は `error` |
| `ShiftContest(contestID, delta)` | `("abc457", +1) → "abc458"` / `("abc457", -1) → "abc456"` | `<英字接頭辞><数字>` に一致しない・数字が 1 未満になる → `error`。ゼロ詰め幅は元の桁数を下限に保持 (`abc099 → abc100`) |

- `ShiftContest` は `abc` 限定の `ContestNum` を一般化し、`^([a-z]+)(\d+)$` で接頭辞 + 数字に分けて数字だけを増減する。これにより `arc` / `agc` / `ahc` も番号移動でき、前方互換になる (exercise レイアウトでも contest_id は `abc<NNN>` 形式なので同じく動く)。
- `:e <spec>` の解釈は既存の `TaskID` / `Detect` を流用する純粋パーサ:
  - `f` (letter のみ) → `(現 contest_id, "f")`
  - `abc458_f` (`_` を含む) → `("abc458", "f")`
  - それ以外 (`abc458` 単体・空・不正) → `error`

ID 用語は既存要件に準拠: `contest_id` = `abc457` / `contest_num` = `457` / `task_id` = `abc457_d` / `letter` = `d`。

## CLI / TUI 仕様

新しいサブコマンドやフラグは**増やさない**。すべて `atcoder start <contest> --task <task>` の分割画面下ペインの**コマンドモード内**で完結する。

### コマンド一覧 (コマンドモードに追加)

`Esc` で insert → command (`:` プロンプト) に入り、以下を打って `Enter` で実行 → insert に戻る。

| コマンド (別名) | 動作 | 例 |
|---|---|---|
| `:task next` (`:task n`) | 問題記号を次へ (letter +1) | `abc457_d` → `abc457_e` |
| `:task prev` (`:task p`) | 問題記号を前へ (letter −1) | `abc457_d` → `abc457_c` |
| `:contest next` (`:contest n`) | コンテストを次へ (contest_num +1、letter 保持) | `abc457_d` → `abc458_d` |
| `:contest prev` (`:contest p`) | コンテストを前へ (contest_num −1、letter 保持) | `abc457_d` → `abc456_d` |
| `:e <spec>` | 任意の問題へジャンプ | `:e f` / `:e abc500_d` |

> 旧文法 (`:next`/`:prev`/`:fwd`/`:back` および別名 `:n`/`:p`/`:f`/`:b`) は廃止し、上の `:task`/`:contest` + 方向トークンに置き換えた。

- 第 1 トークンは `task` / `contest` の**フルワードのみ** (1 文字略語は設けない。`:c` は既存の `:case` と衝突するため)。第 2 トークンは方向で、`next`/`n` と `prev`/`p` を受ける。
- `:task` / `:contest` を第 2 トークン無し・不正トークンで打つと `E492` で利用法を案内し、**再ターゲットせず継続**する (start は落ちない・exit code 不変)。
- これらは**分割画面 (start) の chat でのみ**有効。`test --interactive` 単体の chat では従来どおり**未知コマンド** (`E492: unknown command`) として無視される (ナビ対象の start セッションが無いため)。
- 既存コマンド (`:case`/`:w`/`:set`/`:q`) と `Ctrl+C` (中断・再起動 [025]) / `Ctrl+D` (終了 [022]) / `Ctrl+S` (提出準備 [026]) は不変。

### 処理ステップ (移動 1 回)

1. コマンドモードで `:task next` 等を `Enter`。chat が引数を**純粋パース**して `NavRequest` (種別 + `:e` の spec) を作り、親へ通知 (`NavMsg`)。
2. 親 `startSplitModel` が、注入された **解決関数** `Navigate(現 contest_id, 現 task, req)` を呼ぶ。解決関数 (cmd 側) は:
   1. `ShiftLetter` / `ShiftContest` / `:e` パーサで**新しい `(contest_id, task)`** を算出。境界・不正なら `error`。
   2. `resolveLayout` (現在の flag/env/config を保持、`auto` は新 contest_id で再判定) で layout を決め、`SolutionPath` を得る。
   3. `ensureSolutionFile` で**着手** (親 dir 作成 + 無ければ空ファイル。既存は温存)。
   4. 新 contest/task に束ねた `Spawn` / `ChatHeader` / `SampleRunner` / `Watcher` / `SolutionPath` を組み、`StartTarget` として返す。
3. 親が `StartTarget` を適用:
   - 走っている chat の子を kill し、新 `Spawn` / `Header` で chat サブモデルを**作り直す** (現在のウィンドウサイズで再レイアウト、遅延起動は維持)。
   - watch ペインの要約を「未判定」に戻し、新 `SampleRunner` を 1 回回して要約を更新 (初回判定で lazy fetch)。
   - chat に `(→ abc458_d に移動しました)` の info 行を出す。
4. **解決が `error`** (境界 / 非対応 / 不正 spec) の場合は再ターゲットせず、コマンドラインに 1 行エラーを出して insert に戻る (chat はそのまま継続、exit しない)。
5. `--until-pass` 指定時は、移動後の**新しい問題**に対して全通過判定が適用される。

### 画面イメージ

```
┌ watch ─ abc/457/d.py ─────────────────────────────────┐
  ✓ PASS  3/3        judged 12:34:56
└───────────────────────────────────────────────────────┘
┌ interactive (auto-restart) ───────────────────────────┐
  > 5
  10
  :task next       ← Esc → `:task next` を入力
└───────────────────────────────────────────────────────┘

  ↓ :task next 実行後 (abc457_e へ着手・再ターゲット)

┌ watch ─ abc/457/e.py ─────────────────────────────────┐
  …  (未判定 → 初回判定でサンプル取得)
└───────────────────────────────────────────────────────┘
┌ interactive (auto-restart) ───────────────────────────┐
  (→ abc457_e に移動しました)
  > _
└───────────────────────────────────────────────────────┘
```

## 動作仕様

| 状況 | 挙動 |
|---|---|
| `:task next` / `:task prev` | letter ±1。新 task で着手 → watch/chat を再ターゲット |
| `:contest next` / `:contest prev` | contest_num ±1 (letter 保持)。新 contest_id で着手 → 再ターゲット |
| `:task` / `:contest` 第 2 トークン無し・不正 | `E492` で利用法を案内・再ターゲットせず |
| `:e f` | 現 contest の letter `f` へ。`:e abc500_d` は contest ごとジャンプ |
| 移動先ファイルが無い | **空ファイルを作成** (着手)。`created: <path>` を info 行で示す |
| 移動先ファイルが既にある | 上書きせず温存 (`solution: <path> (exists)`)。提出コードを壊さない |
| letter が `a` で `:task prev` | 再ターゲットせず「これより前の問題はありません」を表示 |
| contest_num が下限で `:contest prev` | 再ターゲットせず「これより前のコンテストはありません」を表示 |
| 番号を持たない contest で `:contest next`/`:contest prev` | 「このコンテストは番号移動に対応していません」を表示 |
| 複数文字 letter で `:task next`/`:task prev` | 「この問題は記号移動に対応していません」を表示 |
| `:e` の引数が空 / 不正 | `E492` 相当のエラー行を表示 (副作用なし) |
| 移動中に走っていた chat の子 | kill して新問題で作り直す (新セッション)。watch ペインも新問題に切替 |
| `--until-pass` | 移動後の新問題に対して全通過で `exit 0` |
| `test --interactive` 単体の chat | `:task`/`:contest` 等は**未知コマンド** (機能無効)。既存挙動を一切変えない |

- **既存非破壊**: `:task`/`:contest` 等を打たない限り start / chat の挙動は従来どおり ([018]〜[026])。`test --watch` / `test --interactive` 単体・他サブコマンドは不変。
- **解答ファイル安全**: 移動先の既存ファイルは絶対に上書きしない (着手は無いときの空ファイル生成のみ)。`--refresh` 相当の再 fetch はしない。
- **stdout 非汚染**: 再ターゲットも分割画面内で完結し、bubbletea が端末を所有。サンプル判定は捕捉 Reporter (`SummaryReporter` [023]) 経由のみ。
- **stale 結果の破棄**: 再ターゲットには**世代タグ (target epoch)** を持たせ、旧問題の遅延サンプル結果・旧 chat stream の残響は不一致で破棄する (chat の `sessionN` [022-S] / startsplit の in-flight 抑止と同方式)。

## 影響範囲

| ファイル / パッケージ | 変更内容 |
|---|---|
| `internal/layout/layout.go` | 純粋関数 `ShiftLetter(letter, delta)` / `ShiftContest(contestID, delta)` を追加。`ContestNum` を内部で `ShiftContest` の接頭辞 + 数字分割に揃える (公開挙動は不変) |
| `internal/layout/layout_test.go` | `ShiftLetter` / `ShiftContest` のテーブルテスト (増減・境界 `a`/`1`・ゼロ詰め幅・非数値 contest・複数文字 letter) |
| `internal/ui/chat.go` | コマンドモードのパーサに `:task next|prev` (`:task n|p`) / `:contest next|prev` (`:contest n|p`) / `:e` を追加。`ChatHeader.NavEnabled` が真のときだけ受理し、純粋パース結果を `NavMsg` として emit。偽なら従来どおり `E492`。`:e` の spec パースは純粋関数に分離 |
| `internal/ui/startsplit.go` | `NavMsg` を親で受けて再ターゲット。`StartSplitConfig` に現 `ContestID`/`Task` と解決関数 `Navigate` を追加。watch 要約リセット + 新 `SampleRunner` 実行 + chat サブモデル作り直し + target epoch 管理 |
| `internal/ui/chat_test.go` / `startsplit_test.go` | nav コマンドのパース (`parseNavCommand`)・`:e` spec パース・target epoch 切替の純粋部分をユニットテスト |
| `cmd/atcoder/start.go` | 初期起動とナビ解決を共通化する `buildTarget(contestID, task) (ui.StartTarget, error)` を切り出し、初回は直接・ナビ時は `Navigate` 経由で呼ぶ。`ensureSolutionFile`/`resolveLayout`/`buildOpts` を再利用 |
| `cmd/atcoder/start_test.go` | `buildTarget` の純粋部分 (ID 算出・境界) のユニットテスト (TUI 本体は手動確認) |
| `docs/tools/usage/start.md` | コマンドモードのナビゲーション一覧・画面イメージを追記 |
| `docs/tools/usage/test.md` | コマンドモード節 (024 で追記) に「ナビは start 限定」を 1 行注記 |
| `docs/tools/todo.md` | 項目 P (start) にナビゲーションの追記節を足し、本要件へ相互リンク |

### API 素描

```go
// internal/layout — layout に依存しない ID 操作 (ContestNum/TaskID/Letter の仲間)。

// ShiftLetter は単一文字 letter を delta だけずらす。
//   ("d", +1) → "e" / ("d", -1) → "c"
// 結果が 'a' 未満になる・letter が単一 a..z でない場合は error。
func ShiftLetter(letter string, delta int) (string, error)

// ShiftContest は <英字接頭辞><数字> 形式の contest_id の数字部を delta だけずらす。
//   ("abc457", +1) → "abc458" / ("abc457", -1) → "abc456"
// ゼロ詰め幅は元の桁数を下限に保持 (abc099 → abc100)。数字が 1 未満になる・
// 形式に一致しない場合は error。
func ShiftContest(contestID string, delta int) (string, error)


// internal/ui — chat はパースして通知するだけ。再ターゲットは親が握る。

// NavKind はナビゲーションの種別。
type NavKind int
const (
    NavLetterNext NavKind = iota // :task next
    NavLetterPrev                // :task prev
    NavContestNext               // :contest next
    NavContestPrev               // :contest prev
    NavExplicit                  // :e <spec>
)

// NavRequest は chat がパースしたナビゲーション要求。Spec は NavExplicit のときの :e 引数。
type NavRequest struct {
    Kind NavKind
    Spec string
}

// NavMsg は chat が親 (startSplitModel) に渡す tea.Msg。NavEnabled が真のときだけ発火。
type NavMsg struct{ Req NavRequest }

// StartTarget は分割画面 1 つ分のターゲット (初期起動・再ターゲット共通)。
type StartTarget struct {
    ContestID, Task string
    SolutionPath    string
    Spawn           Spawner
    Header          ChatHeader   // NavEnabled=true で渡す
    RunSamples      SampleRunner
    Watcher         *watch.Watcher
}

// Navigate は現ターゲットと要求から次のターゲットを解決する (cmd/atcoder が注入)。
// 境界・非対応・不正 spec は error。internal/ui は中身を知らない。
type Navigate func(contestID, task string, req NavRequest) (StartTarget, error)
```

- **層境界**: `internal/ui` は `cmd/atcoder` を import できない ([026] と同方針)。layout 解決・ファイル生成・runner spawn を含む `Navigate` は `cmd/atcoder/start.go` が組み立てて `StartSplitConfig` 経由で注入する。chat は純粋パース → `NavMsg` まで。
- **chat 再利用**: 再ターゲットは `startSplitModel` が `chatModel` を作り直すことで実現し、`chatModel` 自体の公開 API は増やさない (`NavEnabled` フラグと `NavMsg` 発火のみ追加)。

## エラーハンドリング

ナビゲーションは**分割画面の中**で起きるので、失敗は TUI 内の 1 行表示に留め、プログラムは落とさない・exit code は変えない (start 全体の終了は `Ctrl+C` / `--until-pass` 全通過 = 0 のまま)。

| 状況 | 動作 | exit |
|---|---|---|
| `:task prev` で letter が `a` 未満 | 「これより前の問題はありません」を表示・再ターゲットせず | (継続) |
| `:contest prev` で contest_num が下限 | 「これより前のコンテストはありません」を表示・再ターゲットせず | (継続) |
| 番号を持たない contest で `:contest next`/`:contest prev` | 「番号移動に対応していません」を表示 | (継続) |
| 複数文字 letter で `:task next`/`:task prev` | 「記号移動に対応していません」を表示 | (継続) |
| `:task` / `:contest` を第 2 トークン無し・不正トークンで | `E492` で利用法を案内・再ターゲットせず | (継続) |
| `:e` の引数が空 / 不正 | `E492` 相当のエラー行 (副作用なし) | (継続) |
| 移動先 dir 作成 / 空ファイル生成失敗 (権限等) | エラー行を出し再ターゲット中止。chat は継続 | (継続) |
| 移動後のサンプルが取得不可 (テスト無し等) | watch ペインに「判定不可」を表示し続行 ([023] と同じ) | (継続) |
| `test --interactive` 単体で `:task`/`:contest` 等 | `E492: unknown command` (機能無効) | (継続) |

- CLI 引数誤り (`<contest>` / `--task` 欠落等) の exit 2 規約は start 起動時の話で不変。ナビは起動後の TUI 内操作なので exit code レイヤとは別。

## 非機能要件

- **薄い orchestration**: 新しい fetch / judge / chat ロジックを増やさない。`layout` の ID 操作・`ensureSolutionFile`・`testexec`・`ui.RunStartSplit` を束ねるだけ。
- **既存非破壊・前方互換**: `:task`/`:contest` 等を打たない限り [018]〜[026] の挙動は不変。`StartSplitConfig` への追加は任意フィールド (`Navigate`/`ContestID`/`Task`)、`ChatHeader.NavEnabled` の既定 false で `test --interactive` は無影響。`ContestNum` の内部共通化は公開挙動を変えない。
- **解答ファイルを壊さない**: 移動先既存ファイルは温存。着手は空ファイル生成のみ。`--refresh` 相当の再取得はしない。
- **端末キー堅牢性**: トリガーは受信確実な `Esc` → `:` コマンド ([ADR 0007])。`Alt`/`Shift`+矢印や `Ctrl`+記号など raw モードで受信不能なキーに依存しない。
- **決定的にテストできる部分は純粋関数に**: `ShiftLetter`/`ShiftContest`/nav コマンドパース/`:e` spec パース/target epoch 切替をユニットテスト。再ターゲットの TUI 駆動・子プロセス I/O は TTY 必須で手動確認 ([023] と同方針、`fixtures/run.sh` は非 TTY = exit 2 のみ assert で不変)。

## 将来の拡張ポイント

- **未着手スキップ**: `:task next` を「次の**まだ解いていない** letter」へ飛ばす変種 (`review` のデータを参照)。
- **連続移動**: `:contest next 3` で 3 つ先の contest へ。
- **テンプレート着手 (H)**: 移動時の空ファイル生成をテンプレート流し込みに差し替え (`ensureSolutionFile` のフックを共有しているので 1 か所で効く)。
- **`test --watch` への横展開**: 分割画面でない watch ループにも同等のナビを載せる (キー設計は別途)。
- **`:e` の補完・履歴**: コマンドモードでの候補表示。
- **ラップアラウンド**: 上限 letter で `:task next` → 次 contest の `a` へ折り返すオプション。

## 用語

- **ナビゲーション (移動)**: 分割画面に居たまま現在の問題から隣の問題 (letter ±1 / contest ±1 / 任意ジャンプ) へ切り替える操作。
- **再ターゲット (retarget)**: 移動先の問題に合わせて watch ペインのサンプル判定・chat ペインの子プロセス・解答パスを作り直すこと。
- **着手 (start)**: 親 dir 作成 → 解答ファイル生成 (無ければ空) の一連 ([018])。
- `contest_id` = `abc457` / `contest_num` = `457` / `task_id` = `abc457_d` / `letter` = `d` (既存要件に準拠)。

## 関連ドキュメント

- `docs/tools/requirements/018-start-command.md` (start 本体・`ensureSolutionFile`・着手セマンティクス)
- `docs/tools/requirements/023-start-split-screen.md` (分割画面 `startSplitModel` / `RunStartSplit` / `SummaryReporter` — 本要件の再ターゲット基盤)
- `docs/tools/requirements/024-interactive-case-builder.md` (vim 風コマンドモードの土台 — 本要件が `:task`/`:contest` 等を足す)
- `docs/tools/requirements/002-exercise-abc-layout.md` (`ContestNum`/`TaskID`/`Letter` などの ID 操作)
- `docs/tools/requirements/017-config-layout-default.md` (`resolveLayout` の precedence — 移動時に保持)
- `docs/tools/requirements/026-chat-submit.md` (層境界: `internal/ui` はコールバック/メッセージで `cmd/atcoder` と疎結合)
- `docs/tools/decisions/0007-interactive-command-mode-trigger.md` (`Esc` トリガー・受信不能キーの罠)
- `docs/tools/usage/start.md` (利用手引・実装時にナビゲーションを追記)
</content>
</invoke>
