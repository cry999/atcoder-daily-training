package testexec

type Reporter interface {
	Fetching(contest, task string)
	Header(task, contest string, timeLimitMs, timeoutMs, ntests int)
	Case(cr CaseResult)
	Summary(passed, total int)
}
