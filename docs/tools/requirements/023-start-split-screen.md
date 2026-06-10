# `atcoder start` 分割画面 (chat + watch 同時動作) 要件定義

> **追記 ([028](028-start-watch-per-case.md)):** watch ペインの要約を「PASS/FAIL 件数 + 失敗ケース番号」から **per-case verdict** (`01 AC  02 WA  03 TLE  04 AC`) 表示に拡張した。`SummaryReporter.Result()` は `(passed, total, cases []CaseResult)` を返し、上ペインは各ケースの合否を AC/WA/TLE/RE で横並びに出す (幅超過は `…` 切り詰め、3 行維持)。下の画面イメージ (`✓ PASS 3/4  fail: 02`) は旧表示で、現行は 028 を参照。

## 概要

`atcoder start` の TTY 体験を**上下分割の 1 画面**にする。**下ペイン = 対話 chat**(解答と live 対話)、**上ペイン = watch 要約**(保存検知でサンプルを自動再判定し、PASS/FAIL と失敗ケースをコンパクト表示)。chat と watch を**同時に動かし続け**、対話しながら編集 → 保存するたびに上ペインのサンプル判定が自動更新される。現状の「`i` で chat に入ると watch が止まり、chat を抜けないと watch に戻れない」というモード切替を廃し、両方を常時並走させる。

## 背景・目的

- `atcoder start` は「着手して watch で回しつつ、必要なら `i` で対話」という流れだが、**対話中は watch が止まる**。対話で挙動を確かめながら「サンプルは今どうなっているか」を見るには、毎回 chat を抜けて watch に戻る必要がある。
- 対話問題やデバッグ中は「手で動かす (chat)」と「サンプル自動判定 (watch)」を**同時に**見たい。1 画面に合成すれば、編集 → 保存 → 上ペインが即更新、を対話を続けたまま確認できる。
- start は既に TTY 必須。分割画面 (bubbletea) 前提で設計できる。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 対象 | `atcoder start` の **TTY 経路のみ** (start は元々 TTY 必須) | — |
| レイアウト | **上下 2 分割** (上=watch 要約・下=chat) | 左右分割・ペイン比率の調整キー |
| 起動 | **start 起動時から常に分割画面** (旧来の `i` でモード遷移する形は廃止) | `--no-split` で旧来の watch ループに戻すフラグ |
| watch ペイン | サンプル判定の**コンパクト要約** (PASS/FAIL 件数 + 失敗ケース番号 + 最終判定時刻)。diff は出さない | ペイン内に diff を出すトグル |
| chat ペイン | 既存 chat (auto-restart で起動・子終了で自動再実行) を再利用 | — |
| 再判定の契機 | 解答ファイルの**保存検知** (mtime) で上ペインを自動再判定 | 手動再判定キー |
| 終了 | `Ctrl+C` で全体終了 (exit 0)。`--until-pass` ならサンプル全通過で終了 | — |
| 副作用 | 解答・キャッシュ・git を壊さない (既存 start と同じ) | — |

### 境界

- chat ペインの子プロセスと watch ペインのサンプル判定は**独立した別実行**だが、保存検知では**両方**が新コードを反映する: 上ペインはサンプルを再判定し、下ペインの chat も最新コードで reload する (`test --interactive` の watch-reload と同方針)。chat の reload は `ChatHeader.WatchPath` を渡して有効化する。
- 非 TTY では start は元々 `exit 2` (TTY 必須)。分割画面も TTY 専用。

## CLI 仕様

```
atcoder start <contest> --task <task> [--until-pass] [--refresh] [-d] [-s] [-j <n>] [--timeout <dur>] [--tolerance <eps>] [--layout <...>]
```

- フラグは現状の `start` から不変 (新フラグは足さない)。挙動だけ「常時分割画面」に変わる。
- `--until-pass`: 上ペインのサンプル判定が全通過したら分割画面を閉じて `exit 0`。

### 画面イメージ

```
┌ watch ─ exercise/2026/06/11/abc999_a.py ──────────────┐
  ✓ PASS  3/4   fail: 02    judged 12:34:56
└───────────────────────────────────────────────────────┘
┌ interactive (auto-restart) ───────────────────────────┐
  > 5
  10
  > _
└───────────────────────────────────────────────────────┘
  Enter 送信 · Ctrl+D 子 stdin を閉じる · Ctrl+C 終了 · 保存で上を再判定
```

(枠は概念図。実装は lipgloss で軽く装飾し、上=watch 要約 / 下=chat / 最下部にキーヘルプ。)

### 処理ステップ

1. `start` の解答ファイル用意・layout 解決は現状どおり。
2. TTY なら**分割画面 bubbletea プログラム** (`ui.RunStartSplit`) を起動する (旧 `runStartWatch` の命令的ループ + `waitForAction` raw-tty 多重化は廃止)。
3. プログラムは:
   - chat サブモデル (auto-restart) を下ペインに生成・駆動 (子プロセスと live I/O)。
   - 起動時に 1 回サンプル判定を走らせ、上ペインに要約を出す。
   - `tea.Tick` で mtime をポーリングし、保存を検知したらサンプル再判定 Cmd を発火 → 要約を更新。
   - サンプル判定は **stdout に出さず**、捕捉用 Reporter で結果を集めて要約文字列にする。
4. `Ctrl+C` で全体終了。`--until-pass` 時は全通過の要約を受けたら終了。

## 動作仕様

| 状況 | 挙動 |
|---|---|
| start 起動 (TTY) | 上下分割画面。上=watch 要約 (起動時に 1 回判定)、下=chat (auto-restart で対話開始) |
| 解答ファイル保存 | 上ペインのサンプル判定を再実行して要約更新。下ペインの chat も最新コードで reload (test --interactive と同方針) |
| キー入力 | 下ペインの chat 入力へ送る (Enter で子へ送信、`↑`/`↓` 履歴、Ctrl+D で子 stdin close) |
| `Ctrl+C` | 全体を終了 (exit 0)。chat の子も止める |
| chat の子が終了 | auto-restart で再実行 (下ペインに区切り)。watch ペインは無関係に動き続ける |
| `--until-pass` + 全通過 | 分割画面を閉じて exit 0 |
| 端末リサイズ | 上ペイン高さを保ち、下 (chat) に残りを割り当て直す |
| 非 TTY | start は元々 exit 2 (TTY 必須) |

- **既存非破壊**: `test --watch` / `test --interactive` 単体・他サブコマンドは不変。変わるのは `atcoder start` の TTY 体験のみ。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `cmd/atcoder/start.go` | TTY 経路を `ui.RunStartSplit(...)` 呼び出しに置換。旧 `runStartWatch` の命令ループ・`waitForAction`/`waitMtimeOnly`/`keyToAction`/`actInteractive` 等を撤去。解答準備・layout・`--until-pass`・buildOpts はサブ関数として残し、分割モデルへ注入 |
| 新規 `internal/ui/startsplit.go` | 上下分割の bubbletea モデル `startSplitModel` + `RunStartSplit(...)`。watch ペイン状態 + chat サブモデルを保持し、mtime ポーリング Tick・サンプル再判定 Cmd・レイアウト合成を担う |
| `internal/ui/chat.go` | `chatModel` を**サブコンポーネントとして再利用可能**にする最小調整 (割り当て高さを受けてレイアウトする・全体終了は親が判断)。公開 API を増やさず内部で完結させる |
| 新規 `internal/testexec` の捕捉 Reporter | `Reporter` 実装で per-case の Name/Status と Summary(passed,total) を集め、stdout に出さず**構造化要約**を返す (`SummaryReporter`)。`testexec.Run` を bubbletea Cmd 内から呼ぶのに使う |
| `internal/watch` | 既存の `Watcher.Changed()` を流用 (非ブロッキング poll)。追加なし想定 |
| `cmd/atcoder/start_test.go` | 純粋関数 (要約フォーマット・レイアウト高さ計算) のユニットテスト。TUI 本体は TTY 必須で手動確認 |
| `fixtures/run.sh` | start は TTY 必須 → 非 TTY で `exit 2` の smoke を確認 (既存の TTY 必須 smoke を流用・分割化で壊れないこと) |
| `docs/tools/atcoder-start-usage.md` | 分割画面の説明・画面イメージ・キー操作に書き換え |
| `docs/tools/todo.md` | 項目 P (start) に分割画面化を追記、本要件へ相互リンク |

### `internal/ui/startsplit.go` の責務 (素描)

```go
package ui

// SampleRunner は保存検知時に呼ぶサンプル判定 (testexec.Run を捕捉 Reporter で包んだもの)。
// 上ペイン要約に必要な結果だけ返し、stdout には一切書かない。
type SampleRunner func() SampleSummary

// SampleSummary は watch ペインのコンパクト要約。
type SampleSummary struct {
    Passed, Total int
    Failing       []string  // 失敗ケース名 (例 "02")
    AllPassed     bool
    At            time.Time // 判定時刻
    Err           error     // 判定自体が失敗 (テスト無し等)
}

// StartSplitConfig は分割画面の起動設定。
type StartSplitConfig struct {
    SolutionPath string
    Spawn        Spawner       // chat 用の子プロセス起動 (auto-restart)
    Header       ChatHeader    // AutoRestart=true で渡す
    RunSamples   SampleRunner  // 保存検知時のサンプル再判定
    Watcher      *watch.Watcher
    UntilPass    bool
}

// RunStartSplit は上下分割の bubbletea プログラムを駆動する。
// 戻り値: 終了コード (Ctrl+C / --until-pass 全通過 = 0)。
func RunStartSplit(cfg StartSplitConfig) (int, error)
```

- **chat 再利用**: `startSplitModel` は `chatModel` を下ペインとして保持し、`WindowSizeMsg` は上ペイン高さを引いた高さを chat へ転送、`KeyMsg`/`chatLineMsg`/`streamEndMsg` は chat へ委譲、chat の Cmd を親 Update から伝播する。`Ctrl+C` だけ親が握って全体終了。
- **保存検知**: `tea.Tick(pollInterval)` ごとに `Watcher.Changed()` を見て、変化があれば `RunSamples` を回す Cmd を発火 (二重実行は in-flight フラグで抑止)。
- **レイアウト**: `lipgloss.JoinVertical` で上 (watch 要約・固定数行) + 下 (chat・残り高さ) + キーヘルプ。
- **stdout 非汚染**: サンプル判定は捕捉 Reporter 経由でのみ結果を得る。bubbletea 描画と衝突する直接 print をしない。

## エラーハンドリング

| 状況 | 動作 | exit |
|---|---|---|
| 非 TTY | "start requires a terminal" | 2 |
| `--task` 無し / 引数誤り | 既存どおり | 2 |
| サンプルが取得できない (テスト無し等) | 上ペインに「判定不可」を表示し続行 (chat は動く)。プログラムは落とさない | (継続) |
| chat の spawn 失敗 | 下ペインにエラー表示。watch は継続 | (継続) |
| `Ctrl+C` / `--until-pass` 全通過 | 正常終了 | 0 |

## 非機能要件

- **既存非破壊**: `test --watch`・`test --interactive`・他コマンドは不変。`internal/testexec.Run` の既存呼び出し (stdout Reporter) も不変で、捕捉 Reporter は追加実装。
- **stdout を汚さない**: 分割画面中は bubbletea が端末を所有。サンプル判定は捕捉 Reporter のみで、`os.Stdout` に直接書かない。
- **決定的にテストできる部分は純粋関数に**: 要約フォーマット・ペイン高さ計算をユニットテスト。TUI 駆動・子プロセス I/O は TTY 必須で手動確認 (既存 chat / start と同じ方針)。
- **TTY 必須**: 非 TTY は exit 2 (既存維持)。

## 将来の拡張ポイント

- **`--no-split`**: 旧来の全画面 watch ループ (+ `i` で chat) に戻すフラグ。
- **左右分割 / 比率調整**: レイアウトの選択。
- **watch ペイン内 diff トグル**: 失敗ケースの diff をペイン内で開閉。
- **保存で chat も再起動**: 保存検知時に対話セッションも作り直すオプション (現状は中断しない方針)。

## 用語

- **分割画面 (split screen)**: 1 つの bubbletea プログラムが上下 2 ペインを同時描画する状態。
- **watch ペイン**: 上ペイン。保存検知でサンプルを再判定し、PASS/FAIL 要約を出す。
- **chat ペイン**: 下ペイン。既存の対話 chat (auto-restart)。
- **コンパクト要約 (SampleSummary)**: PASS/FAIL 件数 + 失敗ケース名 + 判定時刻。diff を含まない。

## 関連ドキュメント

- `docs/tools/requirements/019-start-key-actions.md` (start の watch + `i` キー: 本要件で分割画面に発展)
- `docs/tools/requirements/020-interactive-auto-restart-flag.md` (chat の auto-restart)
- `docs/tools/atcoder-start-usage.md` (利用手引)
- `docs/tools/atcoder-test-architecture.md` (chat TUI 内部設計)
