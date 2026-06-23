package debugstrip

import "testing"

func TestCommentOut(t *testing.T) {
	tests := []struct {
		name    string
		src     string
		want    string
		wantNum int
	}{
		{
			name:    "double-quoted [DEBUG] print",
			src:     "n = int(input())\nprint(\"[DEBUG] n\", n)\nprint(n)\n",
			want:    "n = int(input())\n# print(\"[DEBUG] n\", n)\nprint(n)\n",
			wantNum: 1,
		},
		{
			name:    "f-string and single-quote variants",
			src:     "print(f\"[DEBUG] {x}\")\nprint('[DEBUG] y')\nprint(answer)\n",
			want:    "# print(f\"[DEBUG] {x}\")\n# print('[DEBUG] y')\nprint(answer)\n",
			wantNum: 2,
		},
		{
			name:    "indentation preserved",
			src:     "for i in range(n):\n    print(\"[DEBUG]\", i)\n    total += i\n",
			want:    "for i in range(n):\n    # print(\"[DEBUG]\", i)\n    total += i\n",
			wantNum: 1,
		},
		{
			name:    "non-debug print untouched",
			src:     "print(\"hello\")\nprint(result)\n",
			want:    "print(\"hello\")\nprint(result)\n",
			wantNum: 0,
		},
		{
			name:    "guarded sole-body print skipped (avoid empty block)",
			src:     "if os.environ.get(\"DEBUG\"):\n    print(f\"[DEBUG] {n}\")\nprint(n)\n",
			want:    "if os.environ.get(\"DEBUG\"):\n    print(f\"[DEBUG] {n}\")\nprint(n)\n",
			wantNum: 0,
		},
		{
			name:    "blank line before guarded print still skipped",
			src:     "if DEBUG:\n\n    print(\"[DEBUG] x\")\n",
			want:    "if DEBUG:\n\n    print(\"[DEBUG] x\")\n",
			wantNum: 0,
		},
		{
			name:    "debug-only block left intact (would empty block)",
			src:     "if DEBUG:\n    print(\"[DEBUG] a\")\n    print(\"[DEBUG] b\")\n",
			want:    "if DEBUG:\n    print(\"[DEBUG] a\")\n    print(\"[DEBUG] b\")\n",
			wantNum: 0,
		},
		{
			name:    "debug print mixed with real code in loop is commented",
			src:     "for i in range(n):\n    print(\"[DEBUG] a\", i)\n    total += i\n",
			want:    "for i in range(n):\n    # print(\"[DEBUG] a\", i)\n    total += i\n",
			wantNum: 1,
		},
		{
			name:    "already commented is idempotent",
			src:     "# print(\"[DEBUG] n\", n)\nprint(n)\n",
			want:    "# print(\"[DEBUG] n\", n)\nprint(n)\n",
			wantNum: 0,
		},
		{
			name:    "no trailing newline",
			src:     "print(\"[DEBUG]\", 1)",
			want:    "# print(\"[DEBUG]\", 1)",
			wantNum: 1,
		},
		{
			name:    "empty source",
			src:     "",
			want:    "",
			wantNum: 0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, n := CommentOut(tt.src)
			if got != tt.want {
				t.Errorf("CommentOut() output mismatch:\n got: %q\nwant: %q", got, tt.want)
			}
			if n != tt.wantNum {
				t.Errorf("CommentOut() count = %d, want %d", n, tt.wantNum)
			}
		})
	}
}

// TestCommentOutIdempotent は 2 回適用しても結果が変わらないことを確認する。
func TestCommentOutIdempotent(t *testing.T) {
	src := "n = int(input())\nprint(f\"[DEBUG] {n}\")\nprint(n)\n"
	once, n1 := CommentOut(src)
	twice, n2 := CommentOut(once)
	if once != twice {
		t.Errorf("not idempotent:\n once: %q\ntwice: %q", once, twice)
	}
	if n1 != 1 || n2 != 0 {
		t.Errorf("counts = (%d, %d), want (1, 0)", n1, n2)
	}
}
