// Package reviewrule parses and evaluates the small condition language used by
// `atcoder review missed`.
package reviewrule

import (
	"fmt"
	"strconv"
	"strings"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/solvestat"
)

// Mode is how multiple conditions are combined.
type Mode string

const (
	ModeAny Mode = "any"
	ModeAll Mode = "all"
)

// DefaultConditions keeps review missed backward-compatible with requirement 074.
var DefaultConditions = []string{"ac=false", "editorial=true"}

// Rule is a parsed set of review conditions.
type Rule struct {
	Mode       Mode
	Conditions []Condition
}

// Condition is a parsed predicate over a solve-stat block.
type Condition struct {
	raw   string
	field string
	op    string
	value string
}

// Parse builds a Rule from config values. Empty conditions mean the default rule.
func Parse(mode string, conditions []string) (Rule, error) {
	m := Mode(strings.TrimSpace(mode))
	if m == "" {
		m = ModeAny
	}
	if m != ModeAny && m != ModeAll {
		return Rule{}, fmt.Errorf("review.missed.mode must be any or all: %q", mode)
	}
	cleaned := cleanConditions(conditions)
	if len(cleaned) == 0 {
		cleaned = DefaultConditions
	}
	r := Rule{Mode: m, Conditions: make([]Condition, 0, len(cleaned))}
	for _, raw := range cleaned {
		c, err := parseCondition(raw)
		if err != nil {
			return Rule{}, err
		}
		r.Conditions = append(r.Conditions, c)
	}
	return r, nil
}

func cleanConditions(in []string) []string {
	var out []string
	for _, s := range in {
		for _, part := range strings.Split(s, ",") {
			if t := strings.TrimSpace(part); t != "" {
				out = append(out, t)
			}
		}
	}
	return out
}

func parseCondition(raw string) (Condition, error) {
	field, op, value, ok := splitCondition(raw)
	if !ok {
		return Condition{}, fmt.Errorf("invalid review condition %q", raw)
	}
	c := Condition{raw: raw, field: field, op: op, value: value}
	switch {
	case field == "ac" || field == "editorial":
		if op != "=" && op != "!=" {
			return Condition{}, fmt.Errorf("invalid review condition %q: bool fields only support = or !=", raw)
		}
		if _, err := strconv.ParseBool(value); err != nil {
			return Condition{}, fmt.Errorf("invalid review condition %q: want true or false", raw)
		}
	case strings.HasPrefix(field, "score."):
		if !knownOp(op) {
			return Condition{}, fmt.Errorf("invalid review condition %q: unknown operator", raw)
		}
		axis := strings.TrimPrefix(field, "score.")
		if !knownAxis(axis) {
			return Condition{}, fmt.Errorf("invalid review condition %q: unknown score axis", raw)
		}
		n, err := strconv.Atoi(value)
		if err != nil || n < 0 || n > 3 {
			return Condition{}, fmt.Errorf("invalid review condition %q: score value must be 0-3", raw)
		}
	case field == "duration":
		if !knownOp(op) {
			return Condition{}, fmt.Errorf("invalid review condition %q: unknown operator", raw)
		}
		if value != "target" {
			if _, err := time.ParseDuration(value); err != nil {
				return Condition{}, fmt.Errorf("invalid review condition %q: duration value must be a duration or target", raw)
			}
		}
	default:
		return Condition{}, fmt.Errorf("invalid review condition %q: unknown field", raw)
	}
	return c, nil
}

func splitCondition(raw string) (field, op, value string, ok bool) {
	raw = strings.TrimSpace(raw)
	for _, candidate := range []string{"!=", "<=", ">=", "=", "<", ">"} {
		if i := strings.Index(raw, candidate); i >= 0 {
			field = strings.TrimSpace(raw[:i])
			op = candidate
			value = strings.TrimSpace(raw[i+len(candidate):])
			return field, op, value, field != "" && value != ""
		}
	}
	return "", "", "", false
}

func knownOp(op string) bool {
	switch op {
	case "=", "!=", "<", "<=", ">", ">=":
		return true
	default:
		return false
	}
}

func knownAxis(axis string) bool {
	switch axis {
	case "knowledge", "translation", "complexity", "impl", "verify":
		return true
	default:
		return false
	}
}

// Match reports whether st satisfies the rule. Missing fields make the
// corresponding condition false.
func (r Rule) Match(st solvestat.Stat) bool {
	if len(r.Conditions) == 0 {
		return false
	}
	if r.Mode == ModeAll {
		for _, c := range r.Conditions {
			if !c.Match(st) {
				return false
			}
		}
		return true
	}
	for _, c := range r.Conditions {
		if c.Match(st) {
			return true
		}
	}
	return false
}

// Match reports whether st satisfies the condition.
func (c Condition) Match(st solvestat.Stat) bool {
	switch {
	case c.field == "ac":
		if st.AC == nil {
			return false
		}
		want, _ := strconv.ParseBool(c.value)
		return compareBool(*st.AC, c.op, want)
	case c.field == "editorial":
		if st.Editorial == nil {
			return false
		}
		want, _ := strconv.ParseBool(c.value)
		return compareBool(*st.Editorial, c.op, want)
	case strings.HasPrefix(c.field, "score."):
		got, ok := scoreValue(st.Score, strings.TrimPrefix(c.field, "score."))
		if !ok || got < 0 {
			return false
		}
		want, _ := strconv.Atoi(c.value)
		return compareInt(got, c.op, want)
	case c.field == "duration":
		if st.DurationMs <= 0 {
			return false
		}
		var want int64
		if c.value == "target" {
			if st.TargetMs <= 0 {
				return false
			}
			want = st.TargetMs
		} else {
			d, _ := time.ParseDuration(c.value)
			want = d.Milliseconds()
		}
		return compareInt64(st.DurationMs, c.op, want)
	default:
		return false
	}
}

func scoreValue(s solvestat.Score, axis string) (int, bool) {
	switch axis {
	case "knowledge":
		return s.Knowledge, true
	case "translation":
		return s.Translation, true
	case "complexity":
		return s.Complexity, true
	case "impl":
		return s.Impl, true
	case "verify":
		return s.Verify, true
	default:
		return 0, false
	}
}

func compareBool(got bool, op string, want bool) bool {
	switch op {
	case "=":
		return got == want
	case "!=":
		return got != want
	default:
		return false
	}
}

func compareInt(got int, op string, want int) bool {
	return compareInt64(int64(got), op, int64(want))
}

func compareInt64(got int64, op string, want int64) bool {
	switch op {
	case "=":
		return got == want
	case "!=":
		return got != want
	case "<":
		return got < want
	case "<=":
		return got <= want
	case ">":
		return got > want
	case ">=":
		return got >= want
	default:
		return false
	}
}

// ParseList parses a comma-separated config-set value into individual conditions.
func ParseList(raw string) []string {
	return cleanConditions([]string{raw})
}

// FormatList returns a stable comma-separated representation for config get/show.
func FormatList(conditions []string) string {
	return strings.Join(cleanConditions(conditions), ",")
}
