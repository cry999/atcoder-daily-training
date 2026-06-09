package testexec

// Reporter はテスト実行の進捗・結果を受け取って表示する。
//
// ライフサイクル:
//
//	Fetching (任意, サンプル取得時のみ)
//	Header
//	Begin(names, jobs)
//	  CaseStarted / CaseFinished  ← ワーカー goroutine から並列・順不同で呼ばれる
//	End(results)                  ← results はケース名順。詳細 (diff/stderr) はここで出す
//	Summary
//
// CaseStarted / CaseFinished は複数 goroutine から同時に呼ばれるため、
// 実装はスレッドセーフでなければならない。
type Reporter interface {
	Fetching(contest, task string)
	Header(task, contest string, timeLimitMs, timeoutMs, ntests int, tolerance float64)
	// Begin はこれから names のケースを jobs 並列で実行することを伝える。
	Begin(names []string, jobs int)
	// CaseStarted はワーカーが name のケースの実行を開始したことを伝える (順不同)。
	CaseStarted(name string)
	// CaseFinished はケースが完了したことを伝える (順不同)。
	CaseFinished(cr CaseResult)
	// End は全ケース完了後に呼ばれる。results はケース名順。
	End(results []CaseResult)
	Summary(passed, total int)
}
