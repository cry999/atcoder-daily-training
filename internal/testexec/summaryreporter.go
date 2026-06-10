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
}

// NewSummaryReporter は空の捕捉 Reporter を返す。
func NewSummaryReporter() *SummaryReporter { return &SummaryReporter{} }

// --- Reporter インタフェース実装 (表示系はすべて no-op) ---

func (r *SummaryReporter) Fetching(contest, task string) {}
func (r *SummaryReporter) Header(task, contest string, timeLimitMs, timeoutMs, ntests int, tolerance float64) {
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
