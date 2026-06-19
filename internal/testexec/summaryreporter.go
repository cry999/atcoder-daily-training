package testexec

import (
	"sync"
)

// SummaryReporter は Reporter のうち per-case の結果と総数だけを捕捉し、stdout には
// 一切書かない。start の分割画面の watch ペインのように、判定結果を「データ」として
// 受け取りたい場面で使う。End は全ケース完了後にケース名順の結果で 1 回呼ばれる。
type SummaryReporter struct {
	mu     sync.Mutex
	cases  []CaseResult // End で受け取るケース名順の全結果
	passed int
	total  int

	// Header で渡るメタ (JSON 出力のトップレベルが必要とする)。捕捉のみで表示しない。
	timeLimitMs int
	timeoutMs   int
	ntests      int
	tolerance   float64
}

// NewSummaryReporter は空の捕捉 Reporter を返す。
func NewSummaryReporter() *SummaryReporter { return &SummaryReporter{} }

// --- Reporter インタフェース実装 (表示系はすべて no-op) ---

func (r *SummaryReporter) Fetching(contest, task string) {}

// Header は表示しないが、JSON 出力用にメタだけ捕捉する (これまで no-op)。
// start.go は Meta() を読まないので既存挙動は不変。
func (r *SummaryReporter) Header(task, contest string, timeLimitMs, timeoutMs, ntests int, tolerance float64) {
	r.mu.Lock()
	r.timeLimitMs, r.timeoutMs, r.ntests, r.tolerance = timeLimitMs, timeoutMs, ntests, tolerance
	r.mu.Unlock()
}
func (r *SummaryReporter) Begin(names []string, jobs int) {}
func (r *SummaryReporter) CaseStarted(name string)        {}
func (r *SummaryReporter) CaseFinished(cr CaseResult)     {}

// End はケース名順の全結果を受け取る。per-case verdict はここで捕捉する。
func (r *SummaryReporter) End(results []CaseResult) {
	r.mu.Lock()
	r.cases = append([]CaseResult(nil), results...)
	r.mu.Unlock()
}

func (r *SummaryReporter) Summary(passed, total int) {
	r.mu.Lock()
	r.passed, r.total = passed, total
	r.mu.Unlock()
}

// Result は捕捉した要約を返す (passed/total と per-case の結果・ケース名順)。
// 失敗ケース名は呼び側で cases から導出する。
func (r *SummaryReporter) Result() (passed, total int, cases []CaseResult) {
	r.mu.Lock()
	defer r.mu.Unlock()
	return r.passed, r.total, append([]CaseResult(nil), r.cases...)
}

// Meta は Header で捕捉したメタ (制限時間・適用 timeout・ケース数・許容誤差) を返す。
// JSON 出力のトップレベルで使う。
func (r *SummaryReporter) Meta() (timeLimitMs, timeoutMs, ntests int, tolerance float64) {
	r.mu.Lock()
	defer r.mu.Unlock()
	return r.timeLimitMs, r.timeoutMs, r.ntests, r.tolerance
}
