package testexec

type Reporter interface {
	Fetching(contest, task string)
	Header(task, contest string, timeLimitMs, timeoutMs, ntests int, tolerance float64)
	Case(cr CaseResult)
	Summary(passed, total int)
}
