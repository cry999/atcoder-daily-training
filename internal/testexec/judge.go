package testexec

import (
	"math"
	"strconv"
	"strings"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/runner"
)

type CaseStatus int

const (
	Pass CaseStatus = iota
	Fail
	TLE
	RE
)

// DebugPrefix で始まる行は、--debug 指定時の比較対象から除外される。
const DebugPrefix = "[DEBUG]"

// DefaultTolerance は float トークンの比較で許容する絶対 / 相対誤差。AtCoder の
// 「絶対誤差または相対誤差が 10^-6 以下なら正解」の慣習に従う。
const DefaultTolerance = 1e-6

type CaseResult struct {
	Name            string
	Status          CaseStatus
	Elapsed         time.Duration
	Input           string // 常にセット (テストケースの標準入力)
	Expected        string // 常にセット (normalize 済みの期待出力)
	Actual          string // 常にセット (normalize 済みの実際の stdout, debug 時は [DEBUG] 行を除外したもの)
	Debug           string // --debug 時にのみセット。[DEBUG] で始まる行の集合
	Stderr          string // RE のみ
	DebugSeen       bool   // 生の stdout / stderr のいずれかに [DEBUG] 始まりの行があったか (提出前ゲート用。要件 044)
	OriginalLimitMs int    // problem の本来の制限時間 (ms)。Status==Pass で Elapsed が超えていたら本来 TLE。
}

// Judge は実行結果の stdout (生) を expected (生) と比較する公開 API。
// `atcoder run --out <file>` のように、testexec のフル test ループに乗らない
// ad-hoc な judge 用途で再利用する。
//   - expected / actual は normalize 前 (改行や末尾空白そのまま) で渡してよい
//   - debug=true なら actual から [DEBUG] 行を取り除いて比較する
//   - tolerance ≤ 0 なら DefaultTolerance を使う
//
// 返り値: 一致したか、正規化済み expected、正規化済み actual、debug 行 (debug=false なら "")。
func Judge(expected, actual string, debug bool, tolerance float64) (pass bool, expectedNorm, actualNorm, debugOut string) {
	if tolerance <= 0 {
		tolerance = DefaultTolerance
	}
	if debug {
		actual, debugOut = splitDebug(actual)
	}
	expN := normalizeOutput(expected)
	actN := normalizeOutput(actual)
	if expN == actN || tokensMatch(expN, actN, tolerance) {
		return true, expN, actN, debugOut
	}
	return false, expN, actN, debugOut
}

func judge(name, input, expected string, pr *runner.ProcessResult, debug bool, tolerance float64) CaseResult {
	if tolerance <= 0 {
		tolerance = DefaultTolerance
	}
	// DEBUG 検出は -d の有無に関係なく、加工前の生 stdout / stderr で見る (要件 044)。
	debugSeen := containsDebugLine(pr.Stdout) || containsDebugLine(pr.Stderr)
	stdout := pr.Stdout
	var debugOut string
	if debug {
		stdout, debugOut = splitDebug(stdout)
	}
	cr := CaseResult{
		Name:      name,
		Elapsed:   pr.Elapsed,
		Input:     strings.TrimRight(input, "\n"),
		Expected:  normalizeOutput(expected),
		Actual:    normalizeOutput(stdout),
		Debug:     debugOut,
		DebugSeen: debugSeen,
	}
	switch pr.Status {
	case runner.TimedOut:
		cr.Status = TLE
	case runner.Exited:
		if pr.ExitCode != 0 {
			cr.Status = RE
			cr.Stderr = pr.Stderr
			break
		}
		if cr.Expected == cr.Actual {
			cr.Status = Pass
			break
		}
		// exact match に失敗したら、float 形式の token は許容誤差つきで再判定する。
		if tokensMatch(cr.Expected, cr.Actual, tolerance) {
			cr.Status = Pass
			break
		}
		cr.Status = Fail
	}
	return cr
}

// tokensMatch は expected / actual を行 → token に分けて比較する。
// expected 側のトークンが float 形式 (. や e/E を含む) のときに限り、
// |exp - act| ≤ tol または |exp - act| ≤ tol · |exp| を許容する。
// 行数 / token 数が不一致なら即 false。
func tokensMatch(expected, actual string, tol float64) bool {
	expLines := strings.Split(expected, "\n")
	actLines := strings.Split(actual, "\n")
	if len(expLines) != len(actLines) {
		return false
	}
	for i := range expLines {
		expToks := strings.Fields(expLines[i])
		actToks := strings.Fields(actLines[i])
		if len(expToks) != len(actToks) {
			return false
		}
		for j := range expToks {
			if !tokenMatch(expToks[j], actToks[j], tol) {
				return false
			}
		}
	}
	return true
}

// tokenMatch は単一トークンを比較する。expected が "." or "e/E" を含むときだけ
// float 許容差を使い、それ以外は厳密文字列一致を要求する。
func tokenMatch(exp, act string, tol float64) bool {
	if exp == act {
		return true
	}
	if !strings.ContainsAny(exp, ".eE") {
		return false
	}
	e, errE := strconv.ParseFloat(exp, 64)
	a, errA := strconv.ParseFloat(act, 64)
	if errE != nil || errA != nil {
		return false
	}
	diff := math.Abs(e - a)
	return diff <= tol || diff <= tol*math.Abs(e)
}

// containsDebugLine は s のいずれかの行が DebugPrefix ([DEBUG]) で始まるかを返す。
// 提出前ゲート (要件 044) で「実行中に DEBUG 出力が漏れていたか」を判定するのに使う。
func containsDebugLine(s string) bool {
	for _, line := range strings.Split(s, "\n") {
		if strings.HasPrefix(line, DebugPrefix) {
			return true
		}
	}
	return false
}

// splitDebug は stdout を「[DEBUG] で始まらない行」と「[DEBUG] で始まる行」に分割する。
func splitDebug(stdout string) (filtered, debug string) {
	var filteredLines, debugLines []string
	for _, line := range strings.Split(stdout, "\n") {
		if strings.HasPrefix(line, DebugPrefix) {
			debugLines = append(debugLines, line)
		} else {
			filteredLines = append(filteredLines, line)
		}
	}
	return strings.Join(filteredLines, "\n"), strings.Join(debugLines, "\n")
}

func normalizeOutput(s string) string {
	s = strings.ReplaceAll(s, "\r\n", "\n")
	return strings.TrimRight(s, "\n")
}
