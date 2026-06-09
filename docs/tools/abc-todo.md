# `exercise` ツールの ABC 本番対応 TODO

## 概要

現状の `exercise` は日々の練習 (`exercise/YYYY/MM/DD/<task>.py`) を前提にしたディレクトリ規約と CLI 体系になっている。これを ABC (AtCoder Beginner Contest) **本番中** にもストレスなく使えるようにするためのロードマップ。

## 背景・狙い

- 本番中は **コンテスト開始直後の準備フリクション** と **WA 後の挙動修正サイクル** が体感に大きく効く。練習用ワークフローのままだと、`exercise new` が当日 dir を作る、`--task` ごとに 1 回ずつ fetch、…と毎回手数が増える。
- 提出 (submit) や認証は `oj` / `atcoder-cli` などの既存ツールに任せれば足りるので、当面ローカル側のフリクション削減に集中する。
- 本ドキュメントは設計の道標であって、各項目の細部仕様は別途要件定義に落とす (`docs/tools/exercise-test-requirements.md` のような形)。

## 優先順位

| フェーズ | 取り組み | 状態 |
|---|---|---|
| MVP | A. ディレクトリ / 命名規約 (`abc/<contest>/<letter>.py` を test/run の対象に) | ✅ DONE (e4b790e) |
| MVP | B. コンテストメタの取り扱い (タスクリストの一括 fetch、コンテストメタ保存) | ✅ DONE (0596725) |
| Phase 2 | E. 本番 vs 練習モード判定 | TODO |
| Phase 2 | F. WA / penalty 後のワークフロー (ユーザ追加ケース) | TODO |
| Phase 2 | G. タイマー / コンテスト状態の TUI | TODO |
| 後回し | C. 提出 (submit) — 当面 `oj` で代替できるので困っていない | TODO |
| 後回し | D. 認証 / セッション管理 — C と同根、同様に低優先 | TODO |
| 別管理 | H. エディタ・テンプレート連携 | ABC 限定でないため `docs/tools/todo.md` に移管 |

---

## MVP

### A. ディレクトリ / 命名規約

#### 解きたい問題

- 今は `exercise test` / `exercise run` ともに、解答ファイルを **当日の `exercise/YYYY/MM/DD/<task>.py`** に決め打ちで探している (`internal/testexec/test.go`, `internal/runexec/runexec.go`)。本番中は `abc/<contest>/<letter>.py` に置きたい。
- 解答ファイルパスの解決ロジックを差し替え可能にする必要がある。

#### 決めること

- 解答パスのレイアウト指定方法
  - 案 1: `--layout abc` / `--layout exercise` フラグで明示切替
  - 案 2: contest プレフィックス (`abc`, `arc`, `agc`) で自動判定
  - 案 3: コンテストメタ (後述 B) に layout を持たせる
  - 候補: **案 2 ベース + 例外時の明示フラグ**。短いコマンドラインを保ちつつ、ADT のような特殊レイアウトには明示で逃げる。
- `--task d` の short form 解決
  - 現状: `<contest>_<task>` に展開 (例 `abc357_d` → ファイル名にも反映)
  - ABC レイアウトでは解答ファイル名は `d.py` だが、AtCoder 上のタスク ID は `abc357_d`。**解答ファイル名と AtCoder の task ID を別に持つ** 設計が必要。
- キャッシュキーは引き続き `<contest>/<task>` (= AtCoder の task ID) で OK か再確認。
- `exercise/YYYY/MM/DD/` ワークフローとの共存ルール (本番中も練習 dir に置きたいケースが本当に無いか)。

#### 影響範囲

- `internal/testexec/test.go` の `solutionPath` 計算
- `internal/runexec/runexec.go` の同等部分
- `cmd/exercise/{test,run}.go` のフラグ追加
- `cmd/exercise/new.go` に `abc <contest>` モード追加 (B と統合して扱う)

### B. コンテストメタの取り扱い

> 要件詳細: `docs/tools/exercise-abc-contest-meta-requirements.md` (`new abc <contest>` 一括準備として設計済み)
>
> **✅ 実装済み (0596725)** — `exercise new abc <contest>` として実装。下記「決めること」は次のように決着した:
> - **コマンド表面**: `contest prepare` 新設ではなく、既存 `exercise new` を拡張して `new abc <contest>` モードにした (引数なしは従来の当日 dir 作成のまま)。
> - **保存場所 / スキーマ**: 候補どおり `$XDG_CACHE_HOME/atcoder-tools/<contest>/contest.toml`。`title` / `fetched_at` を追加し、`start_at` / `end_at` は TOML ネイティブ datetime で保存。
> - **時刻取得元**: `/contests/<contest>` トップページの `contest-duration` 内 `<time class="fixtime">` 2 要素から取得 (`duration_ms` は差分から算出)。タスクリストは `/contests/<contest>/tasks` から。
> - **進捗表示**: `[i/N] <task_id>  ok (fetched/cached)` を 1 行ずつ。ネットワーク取得が起きたタスクの後だけ 300ms 待って rate limit を回避。
> - **`--refresh` / 部分更新**: `--tasks` で部分指定 (全タスクリストは壊さない)、`--refresh` はキャッシュのみ対象で**解答ファイルには一切触れない**。`--no-skeleton` / `--no-fetch` (オフライン) も実装。
> - **スケルトン**: H 未実装のため `abc/<num>/<letter>.py` を**空ファイル**で生成 (既存ファイルは温存)。H 実装時にテンプレート書き込みへ差し替える。
> - **実装**: 新規 `internal/contestmeta/` (スキーマ + load/save + fetch)、`cachepath.Contest`、`layout.ContestNum`、`testexec.EnsureTests` (公開ラッパー)。`fixtures/run.sh` にオフライン smoke + 不正 ID 拒否を追加。
>
> 次の前提: `contest.toml` の時刻メタが揃ったので、E (本番モード判定) / G (タイマー) はこれを入力にできる。

#### 解きたい問題

- 本番では A〜G の問題が一斉に必要になる。今は問題ごとに `exercise test` で都度 fetch するため、開始直後の準備が問題数 × fetch 回数分の手作業になる。
- コンテストの開始 / 終了時刻、参加対象のタスクリストを 1 つの場所に保存しておけば、E (本番モード判定) や G (タイマー) の前提が揃う。

#### 決めること

- 新サブコマンド or 既存拡張
  - 候補: `exercise contest prepare <contest>` を新設。`abc357` を渡すと:
    1. AtCoder の `/contests/<contest>/tasks` を fetch しタスクリスト取得
    2. 各タスクページを fetch しサンプル + meta を cache (= 既存 ensureTests 流用)
    3. `abc/<contest>/<letter>.py` のスケルトンを生成 (H と連動)
    4. コンテストメタを保存
- コンテストメタの保存場所
  - 候補: `$XDG_CACHE_HOME/atcoder-tools/<contest>/contest.toml`
- コンテストメタのスキーマ案
  ```toml
  contest      = "abc357"
  url          = "https://atcoder.jp/contests/abc357"
  start_at     = "2026-06-14T21:00:00+09:00"
  end_at       = "2026-06-14T22:40:00+09:00"
  duration_ms  = 6000000
  tasks        = ["abc357_a", "abc357_b", "abc357_c", "abc357_d", "abc357_e", "abc357_f", "abc357_g"]
  ```
- 開始 / 終了時刻の取得元 (タスク一覧ページから取れる? 取れなければ `/contests/<contest>` トップから)
- バッチ fetch 中の進捗表示 (タスク数 × fetch なのでそれなりに時間が掛かる)
- `--refresh` / 部分更新 (A だけ後から追加など) の挙動

#### 影響範囲

- 新規 `cmd/exercise/contest.go`
- 新規 `internal/contestmeta/` または `internal/testexec` 拡張
- `cmd/exercise/main.go` の usage 更新

---

## Phase 2

### E. 本番 vs 練習モード判定

#### 解きたい問題

- 本番中だけ有効にしたいガード (例: WA を全部 cache してから submit、ペナルティのトラッキング、タイマー表示) を、ユーザがフラグで切り替えるのは面倒。コンテストメタの時刻範囲から自動判定したい。

#### 決めること

- 判定ルール
  - 候補: 現在時刻 ∈ `[contest.start_at, contest.end_at]` かつ解答パスが `abc/<contest>/` 配下なら本番モード。
- フラグで強制切替できるか (`--mode=live` / `--mode=practice`)。CI や後追い AC では `practice` を明示できると便利。
- 本番モード下で挙動が変わるコマンド一覧
  - `test`: 全 PASS でなければ警告強調 (現状もしているが、本番モードでは特に)
  - `run --out`: judge mode で FAIL したケースを「WA 候補」として F のストアに保存
  - `submit` (C 実装後): 全 PASS gate
  - TUI (G): モード表示
- ユーザがどこからモード状態を見られるか (`exercise contest status <contest>` のような diagnostic コマンド)

### F. WA / penalty 後のワークフロー

#### 解きたい問題

- 公式サンプル PASS だけど提出すると WA、というケースで、自分で edge case を書いて再テストする箇所が欲しい。今の cache (`$XDG_CACHE_HOME/atcoder-tools/<contest>/<task>/tests/`) は `--refresh` で上書きされるため、自作ケースを置くと消える。

#### 決めること

- ユーザ追加ケースの保存場所
  - 候補: `$XDG_CACHE_HOME/atcoder-tools/<contest>/<task>/tests-extra/NN.in|NN.out` を作る
  - 候補: リポジトリ内に置く案 (`abc/<contest>/<letter>.tests/NN.in`) — git で履歴が残るが、本番中の作業流れと dir が混ざる
  - 第一候補は cache 配下に専用 dir。`--refresh` で消さない。
- 命名規則: 公式は `01.in` 始まり。ユーザ追加は `e01.in` のように prefix 付け or 別 dir 内で `01.in` 始まり。
- 追加ケースの作り方
  - `exercise test <contest> --task <task> --add-case` でインタラクティブに stdin/expected を入力?
  - シンプルに `tests-extra/` にユーザが直接ファイルを置くだけにする?
  - `exercise run --in foo.in --out foo.out --save-as <name>` で追加保存?
- 追加ケースは公式ケースと同じ判定ループに入れるか、別セクションで表示するか。
- 既存の `exercise test` 出力にユーザ追加ケースをどう混ぜるか (順序、識別子)。

### G. タイマー / コンテスト状態の TUI

#### 解きたい問題

- ブラウザを見ずに残り時間、解いた問題、ペナルティ、現在順位が手元のターミナルでわかると本番では助かる。

#### 決めること

- スコープ
  - 候補 1: シンプルな `exercise contest status <contest>` 1-shot コマンド (残り時間と AC 済みタスクを 1 度だけ表示)
  - 候補 2: bubbletea ベースの live TUI (1 秒ごとに refresh)
  - MVP は **候補 1**。bubbletea はすでに chat TUI で導入しているので Phase 2.5 で候補 2 に拡張可能。
- 表示する情報
  - 必須: 残り時間、参加コンテスト名
  - あれば嬉しい: AC 済みタスク (これは C/D が無いと正確に出せない — `oj` 経由で submission 一覧を引く手も)
- 順位 / ペナルティの取得元 (公式 standings ページのスクレイプ or `oj` の機能 or 自前なし)
- リフレッシュレート、外部 fetch の頻度 (rate limit を踏まないように)

---

## 後回し

### C. 提出 (submit)

`oj` (online-judge-tools) を直接叩けば足りるので困っていない。将来やるなら以下を決める。

- thin wrapper としての `exercise submit <contest> --task d`
  - 内部で `oj submit https://atcoder.jp/contests/<contest>/tasks/<task> <file>` を shell-out
  - `--lang` の上書き、`--yes` で確認スキップ
- 自前実装 (Cookie + CSRF + 言語 ID テーブル) は当面実装しない。`oj` 依存で十分。

### D. 認証 / セッション管理

C と同根。`oj login atcoder` に任せれば自前で Cookie 管理しなくてよい。自前にするなら `$XDG_CONFIG_HOME/atcoder-daily-training/session.json` 保管などを設計するが、当面不要。

---

## 用語

- **layout**: 解答ファイルをどのディレクトリ規約で配置するか。`exercise` (date dir) と `abc` (`abc/<contest>/<letter>.py`) の 2 種を想定。
- **コンテストメタ**: コンテスト単位の情報 (タスクリスト、開始 / 終了時刻、URL)。タスク単位の `meta.toml` とは別に保存する。
- **本番モード / 練習モード**: コンテスト時刻範囲内かつ ABC レイアウト → 本番モード、それ以外 → 練習モード。
