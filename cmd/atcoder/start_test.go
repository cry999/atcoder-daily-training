package main

import (
	"strings"
	"testing"

	"github.com/cry999/atcoder-daily-training/internal/ui"
)

// nextTarget は letter / contest 移動と境界・非対応を要件どおり算出する (純粋部分)。
// TUI 本体 (再ターゲット駆動) は TTY 必須で手動確認。
func TestNextTarget(t *testing.T) {
	cases := []struct {
		name        string
		contestID   string
		task        string
		req         ui.NavRequest
		wantID      string
		wantTask    string
		wantErr     bool
		errContains string
	}{
		{"letter next", "abc457", "abc457_d", ui.NavRequest{Kind: ui.NavLetterNext}, "abc457", "abc457_e", false, ""},
		{"letter prev", "abc457", "abc457_d", ui.NavRequest{Kind: ui.NavLetterPrev}, "abc457", "abc457_c", false, ""},
		{"letter prev at a", "abc457", "abc457_a", ui.NavRequest{Kind: ui.NavLetterPrev}, "", "", true, "これより前の問題はありません"},
		{"letter multi", "abc457", "abc457_xy", ui.NavRequest{Kind: ui.NavLetterNext}, "", "", true, "記号移動に対応していません"},
		{"contest next", "abc457", "abc457_d", ui.NavRequest{Kind: ui.NavContestNext}, "abc458", "abc458_d", false, ""},
		{"contest prev", "abc457", "abc457_d", ui.NavRequest{Kind: ui.NavContestPrev}, "abc456", "abc456_d", false, ""},
		{"contest prev at 1", "abc1", "abc1_d", ui.NavRequest{Kind: ui.NavContestPrev}, "", "", true, "これより前のコンテストはありません"},
		{"contest non-numbered", "dp", "dp_a", ui.NavRequest{Kind: ui.NavContestNext}, "", "", true, "番号移動に対応していません"},
		{"contest next keeps letter & zero-pad", "abc099", "abc099_e", ui.NavRequest{Kind: ui.NavContestNext}, "abc100", "abc100_e", false, ""},
		{"explicit letter", "abc457", "abc457_d", ui.NavRequest{Kind: ui.NavExplicit, Spec: "f"}, "abc457", "abc457_f", false, ""},
		{"explicit contest_letter", "abc457", "abc457_d", ui.NavRequest{Kind: ui.NavExplicit, Spec: "abc500_d"}, "abc500", "abc500_d", false, ""},
		{"explicit empty", "abc457", "abc457_d", ui.NavRequest{Kind: ui.NavExplicit, Spec: ""}, "", "", true, "E492"},
		{"explicit bare contest", "abc457", "abc457_d", ui.NavRequest{Kind: ui.NavExplicit, Spec: "abc500"}, "", "", true, "E492"},
		// 直指定 (:task <letter> / :contest <num|id>) — 要件 031。
		{"task direct letter", "abc457", "abc457_d", ui.NavRequest{Kind: ui.NavLetterExplicit, Spec: "f"}, "abc457", "abc457_f", false, ""},
		{"task direct uppercase", "abc457", "abc457_d", ui.NavRequest{Kind: ui.NavLetterExplicit, Spec: "F"}, "abc457", "abc457_f", false, ""},
		{"task direct invalid", "abc457", "abc457_d", ui.NavRequest{Kind: ui.NavLetterExplicit, Spec: "foo"}, "", "", true, "E492"},
		{"contest direct num", "abc457", "abc457_d", ui.NavRequest{Kind: ui.NavContestExplicit, Spec: "123"}, "abc123", "abc123_d", false, ""},
		{"contest direct num zero-pad keeps letter", "abc457", "abc457_e", ui.NavRequest{Kind: ui.NavContestExplicit, Spec: "5"}, "abc005", "abc005_e", false, ""},
		{"contest direct id keeps letter", "abc457", "abc457_d", ui.NavRequest{Kind: ui.NavContestExplicit, Spec: "arc100"}, "arc100", "arc100_d", false, ""},
		{"contest direct num < 1", "abc457", "abc457_d", ui.NavRequest{Kind: ui.NavContestExplicit, Spec: "0"}, "", "", true, "1 以上"},
		{"contest direct bad form", "abc457", "abc457_d", ui.NavRequest{Kind: ui.NavContestExplicit, Spec: "xyz"}, "", "", true, "E492"},
		{"contest direct on non-numbered", "dp", "dp_a", ui.NavRequest{Kind: ui.NavContestExplicit, Spec: "123"}, "", "", true, "番号指定に対応していません"},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			gotID, gotTask, err := nextTarget(c.contestID, c.task, c.req)
			if c.wantErr {
				if err == nil {
					t.Fatalf("nextTarget(%q,%q,%+v) = (%q,%q,nil), want error", c.contestID, c.task, c.req, gotID, gotTask)
				}
				if c.errContains != "" && !strings.Contains(err.Error(), c.errContains) {
					t.Errorf("error = %q, want it to contain %q", err.Error(), c.errContains)
				}
				return
			}
			if err != nil {
				t.Fatalf("nextTarget(%q,%q,%+v) unexpected error: %v", c.contestID, c.task, c.req, err)
			}
			if gotID != c.wantID || gotTask != c.wantTask {
				t.Errorf("nextTarget = (%q,%q), want (%q,%q)", gotID, gotTask, c.wantID, c.wantTask)
			}
		})
	}
}

func TestParseExplicitSpec(t *testing.T) {
	cases := []struct {
		spec      string
		contestID string
		wantID    string
		wantTask  string
		wantErr   bool
	}{
		{"f", "abc457", "abc457", "abc457_f", false},
		{"D", "abc457", "abc457", "abc457_d", false}, // letter は小文字化
		{"abc500_d", "abc457", "abc500", "abc500_d", false},
		{"arc183_c", "abc457", "arc183", "arc183_c", false},
		{"", "abc457", "", "", true},
		{"abc500", "abc457", "", "", true},  // contest 単体は不可
		{"_d", "abc457", "", "", true},      // contest 部が空
		{"abc500_", "abc457", "", "", true}, // letter 部が空
	}
	for _, c := range cases {
		gotID, gotTask, err := parseExplicitSpec(c.spec, c.contestID)
		if c.wantErr {
			if err == nil {
				t.Errorf("parseExplicitSpec(%q,%q) = (%q,%q,nil), want error", c.spec, c.contestID, gotID, gotTask)
			}
			continue
		}
		if err != nil {
			t.Errorf("parseExplicitSpec(%q,%q) unexpected error: %v", c.spec, c.contestID, err)
			continue
		}
		if gotID != c.wantID || gotTask != c.wantTask {
			t.Errorf("parseExplicitSpec(%q,%q) = (%q,%q), want (%q,%q)", c.spec, c.contestID, gotID, gotTask, c.wantID, c.wantTask)
		}
	}
}
