package main

import (
	"bufio"
	"fmt"
	"os"
	"path/filepath"
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

// submitSource は提出ゲートと提出準備で共有する「提出される中身」(要件 049)。
// 解答を 1 度だけ読み・加工し、ゲートのサンプル実行とクリップボードコピーの両方で
// 同じ Body を使うことで「判定は通ったが別物を提出する」ズレを排除する。
type submitSource struct {
	Path           string // 原本の解答パス (表示・拡張子判定用)
	Body           string // 提出される中身 (keepDebug=false なら [DEBUG] print コメントアウト済み)
	DebugCommented int    // コメントアウトした [DEBUG] 出力行数
}

// buildSubmitSource は解答を読み、keepDebug でなければ [DEBUG] print 行をコメントアウトした
// 「提出される中身」を構築する (要件 049)。解答ファイル本体は読み取りのみで書き換えない。
//
// 返す error: layout/task の解決失敗 (引数誤り) と読込失敗 (実行時失敗) は呼び出し側が
// exit code を振り分けられるよう、解決失敗かどうかを先に切り分けて返す。
func buildSubmitSource(contest, task string, lay layout.Layout, keepDebug bool) (submitSource, error) {
	solutionPath, err := lay.SolutionPath(contest, task)
	if err != nil {
		return submitSource{}, err
	}
	src, err := os.ReadFile(solutionPath)
	if err != nil {
		return submitSource{}, fmt.Errorf("解答ファイルの読み込みに失敗しました: %w", err)
	}
	body := string(src)
	commented := 0
	if !keepDebug {
		body, commented = debugstrip.CommentOut(body)
	}
	return submitSource{Path: solutionPath, Body: body, DebugCommented: commented}, nil
}

// writeTempSource は body を origPath と同じ拡張子の一時ファイルへ書き出し、その絶対パスと
// 後始末関数を返す (要件 049)。拡張子を原本に揃えるのは testexec の ExecutorFor が拡張子で
// 言語を選ぶため。提出ゲートがコメントアウト後ソースを実行対象にするのに使う。
func writeTempSource(origPath, body string) (string, func(), error) {
	f, err := os.CreateTemp("", "atcoder-submit-*"+filepath.Ext(origPath))
	if err != nil {
		return "", nil, fmt.Errorf("一時ファイルの作成に失敗しました: %w", err)
	}
	name := f.Name()
	cleanup := func() { os.Remove(name) }
	if _, err := f.WriteString(body); err != nil {
		f.Close()
		cleanup()
		return "", nil, fmt.Errorf("一時ファイルの書き込みに失敗しました: %w", err)
	}
	if err := f.Close(); err != nil {
		cleanup()
		return "", nil, fmt.Errorf("一時ファイルのクローズに失敗しました: %w", err)
	}
	return name, cleanup, nil
}

// submitPrepCore は印字せずに提出準備の副作用 (解答コピー + 提出ページ起動) を行い
// 結果を返す。chat TUI からも呼べるよう stdout には一切書かない。
//
// 提出する中身は構築済みの submitSource (要件 049) を受け取る — ゲート実行と同じ Body を
// クリップボードへ載せ、判定対象と提出物を一致させる。クリップボード書込の失敗は error。
// ブラウザ起動失敗はコピーが済んでいるので致命的でなく、OpenErr に載せて error にはしない。
func submitPrepCore(src submitSource, contest, task string, noOpen bool) (submitOutcome, error) {
	if err := clipboard.WriteAll(src.Body); err != nil {
		return submitOutcome{}, fmt.Errorf("クリップボードへのコピーに失敗しました: %w", err)
	}
	// meta.toml に URL override があれば、提出先 screen name をそこから決める
	// (best-effort。未取得なら task をそのまま使う)。
	screen := task
	if m, err := testexec.LoadMeta(contest, task); err == nil {
		screen = effectiveScreenName(task, m.URL)
	}
	out := submitOutcome{CopiedPath: src.Path, URL: submitURLFor(contest, screen), DebugCommented: src.DebugCommented}
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

// prepareSubmission は `test --submit` のゲート通過後に呼ばれる提出準備 (CLI 経路)。
// 構築済み中身をクリップボードへコピーし、提出ページをブラウザで開く (best-effort)。
// 実提出 (認証付き POST) はしない — 認証は Turnstile 保護で不可、ブラウザに委ねる (ADR 0006)。
func prepareSubmission(src submitSource, contest, task string, noOpen bool) (int, error) {
	out, err := submitPrepCore(src, contest, task, noOpen)
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

// runSubmitPrep は `test --submit` 本体 (要件 044 / 049)。提出される中身 (コメントアウト
// 後ソース。--keep-debug なら解答そのまま) を一時ファイルに書き出し、それをサンプル判定の
// 実行対象にしてゲートを評価する。クリーンなら確認なしで提出準備、リスクがあれば理由を示し
// 確認を取ってから進む。判定した中身とクリップボードへ載せる中身は同一 (submitSource を共有)。
//
// opts.Reporter にはライブ表示用の Reporter が入っている前提で、それを
// submitGateReporter でラップして DebugSeen を集約する。
//
// exit code は「提出準備に進めたか」を表す: 0=提出準備した / 1=しなかった・失敗 / 2=引数誤り。
func runSubmitPrep(contest, task string, lay layout.Layout, opts testexec.Options, noOpen, keepDebug bool) (int, error) {
	// task/layout の解決失敗は引数誤り (exit 2)。読込・一時ファイル失敗は実行時失敗 (exit 1)。
	if _, err := lay.SolutionPath(contest, task); err != nil {
		return 2, err
	}
	src, err := buildSubmitSource(contest, task, lay, keepDebug)
	if err != nil {
		return 1, err
	}
	tmp, cleanup, err := writeTempSource(src.Path, src.Body)
	if err != nil {
		return 1, err
	}
	defer cleanup()

	gate := &submitGateReporter{Reporter: opts.Reporter}
	opts.Reporter = gate
	opts.SolutionPathOverride = tmp // コメントアウト後ソース (= 提出される中身) を実行する (要件 049)。
	code, runErr := testexec.Run(opts)

	reasons := submitGateReasons(code, runErr, gate.DebugSeen())
	if len(reasons) == 0 {
		// クリーン: 確認なしで提出準備する。
		return prepareSubmission(src, contest, task, noOpen)
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
	return prepareSubmission(src, contest, task, noOpen)
}
