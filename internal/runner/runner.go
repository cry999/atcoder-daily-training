package runner

import "time"

type ProcessStatus int

const (
	Exited ProcessStatus = iota
	TimedOut
)

type ProcessResult struct {
	Status   ProcessStatus
	Stdout   string
	Stderr   string
	Elapsed  time.Duration
	ExitCode int
}
