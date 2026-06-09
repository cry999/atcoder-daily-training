# `atcoder` ツールの一般 TODO

ABC 本番対応に限定されない、`atcoder` ツール全般の改善 TODO。ABC 本番対応のロードマップは `abc-todo.md` を参照。

## H. エディタ・テンプレート連携

### 解きたい問題

- 練習でも本番でも、新規問題ファイルを開いた直後はいつも同じ boilerplate (`import sys; input=sys.stdin.readline`、`from collections import defaultdict` 等) を書くことになり、書き始めまでの摩擦が大きい。
- 練習用の `atcoder new` は当日 dir を mkdir するだけで、ファイルは生成していない。

### 決めること

- テンプレートの所在
  - 候補 1: リポジトリ内 `templates/python.py` (git で履歴管理、共有しやすい)
  - 候補 2: `$XDG_CONFIG_HOME/atcoder-daily-training/templates/python.py` (個人設定として分離)
  - 第一候補は **リポジトリ内**。1 人のリポジトリなので個人設定と区別する利得は薄い。
- テンプレート選択方法
  - 候補: `atcoder new --task d --template default` のように名前指定。デフォルトは "default"。
  - 言語ごとに複数テンプレート (`python_basic.py`, `python_io_fast.py` 等) を持てるようにする。
- 既存ファイルとの衝突
  - 既にファイルがある場合は上書きしない (確認プロンプトもしくは `--force` で上書き)。
- どのコマンドから生成されるか
  - `atcoder new --task d`: 当日 dir に `<task>.py` を生成 (現状は dir のみ作成)
  - ABC 本番対応 (`abc-todo.md` の B) の `contest prepare` でも内部的にこのテンプレート生成を呼ぶ
- テンプレート内の変数展開 (`{{task}}`, `{{contest}}`, `{{date}}` 等を埋め込むか、純粋なテキストか)
- テンプレートの形式 (Go の `text/template` 等を使うか、単純文字列か)

### 影響範囲

- 新規 `templates/` ディレクトリ
- 新規 `internal/template/` パッケージ
- `cmd/atcoder/new.go` の拡張
- ABC ロードマップの B (contest prepare) と接続

### 関連項目

- `abc-todo.md` の B (コンテストメタの取り扱い): contest prepare の中で全タスクのスケルトンを一括生成する。テンプレート機構をそこから呼べるようにしておく。

## I. `test` watch モード ✅ DONE (1105a67)

### 解きたい問題

- 編集ループ中は「コードを直して保存 → ターミナルにフォーカスを戻して `atcoder test ...` を再度叩く」を何十回もくり返す。往復のたびに編集リズムが切れる。
- サンプルは初回 fetch 後はキャッシュにあり、2 回目以降の再実行はネットワーク不要で速い。再実行の起動コストが小さいので、保存検知で自動再実行する watch ループに向いている。

### 決まったこと

> 要件詳細は `docs/tools/requirements/004-exercise-test-watch.md`。

- `atcoder test <contest> --task <task> --watch` (`-w`) で常駐し、解答ファイルの保存を検知して自動再実行する。`Ctrl+C` で終了。
- **監視対象は解答ファイル 1 つだけ** (サンプルや自作ライブラリは将来の拡張)。「保存=再実行」を直感的かつ誤爆なしにするため。
- **検知方式は mtime ポーリング** (200ms, 外部依存なし)。単一ファイル監視には十分で、最小依存方針に合う。atomic save (一旦削除して書き直す) でも再出現時の mtime 変化で拾える。
- **TTY 必須**。画面をクリアして最新結果だけを再描画するため、非 TTY (パイプ/リダイレクト) では exit 2。
- 既存の並列実行 + ライブ進捗表示 (`internal/ui` の bubbletea Reporter) をそのまま各実行に再利用する。
- `--watch` + `--refresh` は**初回のみ** refresh (毎保存での再 fetch を避け rate limit を踏まない)。
- watch の終了コードはループ結果に依存しない (`Ctrl+C` = exit 0)。FAIL/RE/TLE でもループは止めない。

### 影響範囲

- `cmd/atcoder/test.go` (`--watch` 分岐), `cmd/atcoder/main.go` (usage)
- 新規 `internal/watch/` (単一ファイルの mtime ポーリング)
- `internal/ui/` (画面クリア・watch ヘッダ/フッタ)
- `fixtures/run.sh` (非 TTY 拒否 = exit 2 の smoke)

### 関連項目

- ライブ進捗表示・並列実行 (前段の `atcoder test` 改善) の上に乗る。watch は「同じ 1 回実行をループで呼ぶ」薄い層。
- 将来 `atcoder run --watch` へ展開する余地あり (対話/judge モードの再実行)。

## J. 練習統計 (`atcoder stats`) ✅ DONE (dd3c3a8)

### 解きたい問題

- 毎日 `exercise/YYYY/MM/DD/` に解答を積み上げているが、「どれくらい続けられているか」「どの種類に偏っているか」「最近の推移」を振り返る手段が無い。`find | wc -l` を都度叩くしかなかった。
- モチベーション維持にはストリーク (連続練習日数) と推移の可視化が効く。

### 決まったこと

> 要件詳細は `docs/tools/requirements/005-exercise-stats.md`、利用手引は `docs/tools/atcoder-stats-usage.md`。

- `atcoder stats [--week | --month | --year]`。デフォルトは全期間、フラグで今週/今月/今年に絞る (相対指定のみ。任意日付範囲は将来の `--since`/`--until`)。
- **集計対象は `exercise/YYYY/MM/DD/*.py` のみ** (1 ファイル = 1 問、日付はパス由来)。他ツリー横断は将来拡張。
- 統計は解答数・アクティブ日数・current/longest ストリーク・カテゴリ別 (コンテスト種別/レター)・時系列 (週/月は日別、年/全期間は週別)。
- **読み取り専用・オフライン**。ネットワーク・認証・キャッシュ・解答ファイルに一切触れない。
- 集計ロジックは純粋関数 (`internal/stats.Compute`) にして `Now` 注入でユニットテスト。

### 影響範囲

- 新規 `cmd/atcoder/stats.go`, `internal/stats/` (集計 + レンダリング + テスト)
- `cmd/atcoder/main.go` (dispatch + usage)
- `fixtures/run.sh` (exit 0 / 期間フラグ排他 = exit 2 の smoke)
- `docs/tools/atcoder-stats-usage.md` (利用手引)

### 関連項目

- 将来: `--json` 出力、`--since`/`--until`、`adt/` 等の他ツリー横断、難易度/結果別集計。

## K. シェル補完 (`atcoder completion`) ✅ DONE (8118b4d)

### 解きたい問題

- サブコマンドが 6 つ + 多数のフラグに増え、`--task`/`--layout`/`--case` 等を毎回思い出して手打ちするフリクションが大きい。
- 本番・練習ともに `atcoder test abc457 --task d` のように contest_id と letter を頻繁に打つ。番号や letter の打ち間違いが無駄。

### 決まったこと

> 要件詳細は `docs/tools/requirements/007-atcoder-completion.md`。

- `atcoder completion <bash|zsh|fish>` で補完スクリプトを stdout に出力する新サブコマンドを追加。
- **CLI フレームワーク (cobra 等) は導入しない** (標準 `flag` + 手書き dispatch を維持、依存ゼロ追加)。補完だけ手書きで足す。
- **動的補完まで**対応: サブコマンド・フラグの静的補完に加え、`<contest>` (手元の `abc/`・`arc/`・`awc/` + fetch 済みキャッシュ) と `--task` の letter、`--layout` の値を補完。
- 動的候補は隠しヘルパ `atcoder __complete -- <words...>` に集約し、シェルスクリプトは薄いラッパに保つ。`__complete` は**常に exit 0** (補完を壊さない)。
- 読み取り専用・オフライン。CLI 本体の状態や解答ファイルに副作用なし。

### 影響範囲

- 新規 `cmd/atcoder/completion.go`, `internal/complete/` (候補列挙 + テスト)
- `cmd/atcoder/main.go` (dispatch + usage)
- `fixtures/run.sh` (completion 出力 exit 0 / 未対応シェル exit 2 / `__complete` 候補の smoke)
- `docs/tools/atcoder-completion-usage.md` (利用手引)

### 関連項目

- フラグ表は実コード (`cmd/atcoder/*.go`) と手書きで同期する。フラグ追加時は `internal/complete` も更新する。
- 将来: `completion --install`、`--case`/ファイルの補完、powershell 対応、フラグ表のコード生成。
