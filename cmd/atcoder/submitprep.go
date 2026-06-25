package main

import (
	"bufio"
	"fmt"
	"os"
	"strings"
	"sync"

	"github.com/atotto/clipboard"
	"github.com/cry999/atcoder-daily-training/internal/debugstrip"
	"github.com/cry999/atcoder-daily-training/internal/layout"
	"github.com/cry999/atcoder-daily-training/internal/testexec"
	"golang.org/x/term"
)

// submitURLFor は提出ページの URL を組む。
func submitURLFor(contest, task string) string {
	return fmt.Sprintf("https://atcoder.jp/contests/%s/submit?taskScreenName=%s", contest, task)
}

// effectiveScreenName は提出 URL の taskScreenName を決める純粋関数。meta.toml の
// URL override (`atcoder meta set --url`) が task URL として解釈できれば、その task_id
// を screen name に使う。task_id が contest と食い違う問題 (例: abc107 の D = arc101_b、
// 提出先は .../contests/abc107/submit?taskScreenName=arc101_b) で正しい提出先になる。
// override が空 / task URL でなければ task をそのまま使う (contest はここでは変えない)。
func effectiveScreenName(task, urlOverride string) string {
	if urlOverride != "" {
		if _, taskID, ok := layout.ParseTaskURL(urlOverride); ok {
			return taskID
		}
	}
	return task
}

// submitOutcome は提出準備の結果。印字しない core (submitPrepCore) が返し、
// 呼び出し側 (CLI 経路 = 印字 / chat 経路 = 行描画) が好きに表示する。
type submitOutcome struct {
	CopiedPath     string // クリップボードにコピーした解答パス
	URL            string // 提出ページ URL
	Opened         bool   // ブラウザを開けたか (noOpen 時や失敗時は false)
	OpenErr        error  // ブラウザ起動に失敗したときのエラー (noOpen / 成功時は nil)
	DebugCommented int    // クリップボードへ載せる際にコメントアウトした [DEBUG] 出力行数
}

// submitPrepCore は印字せずに提出準備の副作用 (解答コピー + 提出ページ起動) を行い
// 結果を返す。chat TUI からも呼べるよう stdout には一切書かない。
//
// 解答読込・クリップボード書込の失敗は error。ブラウザ起動失敗はコピーが済んで
// いるので致命的でなく、OpenErr に載せて error にはしない。
//
// keepDebug が false (既定) のときは、クリップボードへ載せる前に [DEBUG] を出力する
// print 行をコメントアウトする (解答ファイル本体は書き換えない。加工はメモリ上のみ)。
func submitPrepCore(contest, task string, lay layout.Layout, noOpen, keepDebug bool) (submitOutcome, error) {
	solutionPath, err := lay.SolutionPath(contest, task)
	if err != nil {
		return submitOutcome{}, err
	}
	src, err := os.ReadFile(solutionPath)
	if err != nil {
		return submitOutcome{}, fmt.Errorf("解答ファイルの読み込みに失敗しました: %w", err)
	}
	body := string(src)
	commented := 0
	if !keepDebug {
		body, commented = debugstrip.CommentOut(body)
	}
	if err := clipboard.WriteAll(body); err != nil {
		return submitOutcome{}, fmt.Errorf("クリップボードへのコピーに失敗しました: %w", err)
	}
	// meta.toml に URL override があれば、提出先 screen name をそこから決める
	// (best-effort。未取得なら task をそのまま使う)。
	screen := task
	if m, err := testexec.LoadMeta(contest, task); err == nil {
		screen = effectiveScreenName(task, m.URL)
	}
	out := submitOutcome{CopiedPath: solutionPath, URL: submitURLFor(contest, screen), DebugCommented: commented}
	if noOpen {
		return out, nil
	}
	if err := openBrowser(out.URL); err != nil {
		out.OpenErr = err // コピーは済んでいるので致命的でない。
		return out, nil
	}
	out.Opened = true
	return out, nil
}

// prepareSubmission は `test --submit` のサンプル全通過後に呼ばれる提出準備 (CLI 経路)。
// 解答をクリップボードへコピーし、提出ページをブラウザで開く (best-effort)。
// 実提出 (認証付き POST) はしない — 認証は Turnstile 保護で不可、ブラウザに委ねる (ADR 0006)。
//
// 旧 `atcoder submit` の後半 (サンプルゲート後の処理) を移設したもの。
func prepareSubmission(contest, task string, lay layout.Layout, noOpen, keepDebug bool) (int, error) {
	// task/layout の解決失敗は引数誤り (exit 2)。実体処理の失敗は実行時失敗 (exit 1)。
	if _, err := lay.SolutionPath(contest, task); err != nil {
		return 2, err
	}
	out, err := submitPrepCore(contest, task, lay, noOpen, keepDebug)
	if err != nil {
		return 1, err
	}

	if out.DebugCommented > 0 {
		fmt.Printf("クリップボードにコピーしました: %s (DEBUG 出力 %d 行をコメントアウト)\n", out.CopiedPath, out.DebugCommented)
	} else {
		fmt.Printf("クリップボードにコピーしました: %s\n", out.CopiedPath)
	}
	if noOpen {
		fmt.Printf("提出ページ: %s\n", out.URL)
		return 0, nil
	}
	if out.Opened {
		fmt.Printf("提出ページを開きました: %s\n", out.URL)
	} else {
		fmt.Fprintf(os.Stderr, "ブラウザを開けませんでした (%v)。手動で開いてください: %s\n", out.OpenErr, out.URL)
	}
	return 0, nil
}

// submitGateReporter は testexec.Reporter をラップし、各ケースの DebugSeen を OR で
// 集約する (要件 044)。表示は元の Reporter (ライブ表示 or SummaryReporter) に委譲し、
// 提出前ゲートが「実行中に [DEBUG] 出力が漏れていたか」を後から参照できるようにする。
type submitGateReporter struct {
	testexec.Reporter
	mu        sync.Mutex
	debugSeen bool
}

func (r *submitGateReporter) CaseFinished(cr testexec.CaseResult) {
	if cr.DebugSeen {
		r.mu.Lock()
		r.debugSeen = true
		r.mu.Unlock()
	}
	r.Reporter.CaseFinished(cr)
}

func (r *submitGateReporter) DebugSeen() bool {
	r.mu.Lock()
	defer r.mu.Unlock()
	return r.debugSeen
}

// submitGateReasons はサンプル実行の結果から、提出前に確認を促す理由を組み立てる
// 純粋関数 (要件 044)。返りが空ならクリーン (確認不要)。CLI (runSubmitPrep) と
// chat (chatSubmitCheckFunc) で共有する。
//
// 優先順位: 実行できなかった (runErr) > 全通過でない (code≠0)。実行可否とは独立に、
// DEBUG 出力が検出されていれば理由を追加する。
func submitGateReasons(code int, runErr error, debugSeen bool) []string {
	var reasons []string
	switch {
	case runErr != nil:
		reasons = append(reasons, "テストを実行できませんでした: "+runErr.Error())
	case code != 0:
		reasons = append(reasons, "サンプルが全通過していません")
	}
	if debugSeen {
		reasons = append(reasons, "実行中に [DEBUG] 出力が検出されました")
	}
	return reasons
}

// confirmSubmit は標準入力から提出続行の y/N を読む (要件 044)。stdin が端末でなければ
// (パイプ・CI・fixtures 等) 確認を出さず false (= いいえ) を返す。対話できない環境で
// ブロックせず、安全側 (提出しない) に倒すため。
func confirmSubmit() bool {
	if !term.IsTerminal(int(os.Stdin.Fd())) {
		fmt.Fprintln(os.Stderr, "(非対話環境のため提出準備を中止しました)")
		return false
	}
	fmt.Fprint(os.Stderr, "このまま提出準備を続けますか? [y/N]: ")
	line, _ := bufio.NewReader(os.Stdin).ReadString('\n')
	ans := strings.ToLower(strings.TrimSpace(line))
	return ans == "y" || ans == "yes"
}

// runSubmitPrep は `test --submit` 本体 (要件 044)。サンプルを実行してゲートを評価し、
// クリーンなら従来どおり提出準備、リスクがあれば理由を示して確認を取ってから進む。
//
// opts.Reporter にはライブ表示用の Reporter が入っている前提で、それを
// submitGateReporter でラップして DebugSeen を集約する。
//
// exit code は「提出準備に進めたか」を表す: 0=提出準備した / 1=しなかった・失敗。
func runSubmitPrep(contest, task string, lay layout.Layout, opts testexec.Options, noOpen, keepDebug bool) (int, error) {
	gate := &submitGateReporter{Reporter: opts.Reporter}
	opts.Reporter = gate
	code, runErr := testexec.Run(opts)

	reasons := submitGateReasons(code, runErr, gate.DebugSeen())
	if len(reasons) == 0 {
		// クリーン: 従来どおり確認なしで提出準備する。
		return prepareSubmission(contest, task, lay, noOpen, keepDebug)
	}

	fmt.Fprintln(os.Stderr, "提出前チェックで問題が見つかりました:")
	for _, r := range reasons {
		fmt.Fprintln(os.Stderr, "  - "+r)
	}
	if !confirmSubmit() {
		fmt.Fprintln(os.Stderr, "提出準備を中止しました。")
		// 「提出準備に進めなかった」を 1 で表す (実行エラーの詳細は err で返す)。
		return 1, runErr
	}
	return prepareSubmission(contest, task, lay, noOpen, keepDebug)
}
