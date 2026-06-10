package testexec

import (
	"sort"
	"sync"
)

// SummaryReporter は Reporter のうち per-case の合否と総数だけを捕捉し、stdout には
// 一切書かない。start の分割画面の watch ペインのように、判定結果を「データ」として
// 受け取りたい場面で使う。CaseFinished は複数 goroutine から呼ばれるため mutex で守る。
type SummaryReporter struct {
	mu      sync.Mutex
	failing []string // Pass 以外のケース名
	passed  int
	total   int
}

// NewSummaryReporter は空の捕捉 Reporter を返す。
func NewSummaryReporter() *SummaryReporter { return &SummaryReporter{} }

// --- Reporter インタフェース実装 (表示系はすべて no-op) ---

func (r *SummaryReporter) Fetching(contest, task string) {}
func (r *SummaryReporter) Header(task, contest string, timeLimitMs, timeoutMs, ntests int, tolerance float64) {
}
func (r *SummaryReporter) Begin(names []string, jobs int) {}
func (r *SummaryReporter) CaseStarted(name string)        {}

func (r *SummaryReporter) CaseFinished(cr CaseResult) {
	if cr.Status == Pass {
		return
	}
	r.mu.Lock()
	r.failing = append(r.failing, cr.Name)
	r.mu.Unlock()
}

func (r *SummaryReporter) End(results []CaseResult) {}

func (r *SummaryReporter) Summary(passed, total int) {
	r.mu.Lock()
	r.passed, r.total = passed, total
	r.mu.Unlock()
}

// Result は捕捉した要約を返す (passed/total と失敗ケース名・昇順)。
func (r *SummaryReporter) Result() (passed, total int, failing []string) {
	r.mu.Lock()
	defer r.mu.Unlock()
	f := append([]string(nil), r.failing...)
	sort.Strings(f)
	return r.passed, r.total, f
}
