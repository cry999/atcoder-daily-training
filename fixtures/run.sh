#!/usr/bin/env bash
# fixtures/run.sh -- `exercise test` / `exercise run` のスモークテスト
#
# fixtures/<task>.py を一時ディレクトリの exercise/YYYY/MM/DD/ に置き、
# fixtures/cache/ を XDG_CACHE_HOME に指定することで、ツール本体に
# テスト専用のパス上書き機構を持たせずに各種ステータスを検査する。

set -euo pipefail

cd "$(dirname "$0")/.."
REPO_ROOT="$(pwd)"
FIXTURES="$REPO_ROOT/fixtures"

# Build the tool.
TOOL_DIR="$(mktemp -d)"
trap 'rm -rf "$TOOL_DIR" "$STAGE" "$CACHE_HOME"' EXIT
BIN="$TOOL_DIR/exercise"
echo "Building $BIN ..."
go build -o "$BIN" ./cmd/exercise

# Stage solutions under <stage>/exercise/YYYY/MM/DD/.
STAGE="$(mktemp -d)"
DATE_DIR="exercise/$(date +%Y/%m/%d)"
mkdir -p "$STAGE/$DATE_DIR"
cp "$FIXTURES/"fixture_*.py "$STAGE/$DATE_DIR/"

# Stage an ABC-layout solution at abc/999/a.py so we can exercise --layout=auto/abc.
# Reuses fixture_pass.py (n → n*2). The cache for abc999_a is already pre-populated
# in fixtures/cache/atcoder-tools/abc999/abc999_a/ (input 5 → expected 10).
mkdir -p "$STAGE/abc/999"
cp "$FIXTURES/fixture_pass.py" "$STAGE/abc/999/a.py"

# Stage pre-populated cache (meta.toml + tests/) under a private XDG_CACHE_HOME.
CACHE_HOME="$(mktemp -d)"
cp -R "$FIXTURES/cache/." "$CACHE_HOME/"
export XDG_CACHE_HOME="$CACHE_HOME"

cd "$STAGE"

failures=0
run_case() {
    local label="$1"
    local expected_exit="$2"
    shift 2
    echo
    echo "=== ${label} (expecting exit ${expected_exit}) ==="
    set +e
    "$BIN" "$@"
    local got=$?
    set -e
    if [[ "$got" -ne "$expected_exit" ]]; then
        echo "  ✗ exit ${got} (expected ${expected_exit})"
        failures=$((failures + 1))
    else
        echo "  ✓ exit ${got}"
    fi
}

run_piped() {
    local label="$1"
    local expected_exit="$2"
    local input="$3"
    shift 3
    echo
    echo "=== ${label} (expecting exit ${expected_exit}) ==="
    set +e
    printf '%s' "$input" | "$BIN" "$@"
    local got=$?
    set -e
    if [[ "$got" -ne "$expected_exit" ]]; then
        echo "  ✗ exit ${got} (expected ${expected_exit})"
        failures=$((failures + 1))
    else
        echo "  ✓ exit ${got}"
    fi
}

run_case "fixture_pass"               0 test fixture --task pass
run_case "fixture_fail"               1 test fixture --task fail
run_case "fixture_re"                 1 test fixture --task re
run_case "fixture_tle"                1 test fixture --task tle
run_case "fixture_debug w/o -d"       1 test fixture --task debug
run_case "fixture_debug w/  -d"       0 test fixture --task debug -d
run_case "fixture_multi all"          0 test fixture --task multi
run_case "fixture_multi --case 02"    0 test fixture --task multi --case 02
run_case "fixture_multi -c 1,3"       0 test fixture --task multi -c 1,3
run_case "fixture_multi --case 99"    1 test fixture --task multi --case 99
run_case "fixture_diff (multi-line)"  1 test fixture --task diff
run_case "fixture_float (1e-6 tol)"   0 test fixture --task float

# watch モードは TTY 必須。run.sh の出力は非 TTY なので --watch は exit 2 で拒否される。
# (watch ループ本体は常駐してブロックするため、ここでは回さない。)
run_case "fixture_pass --watch (non-TTY reject)" 2 test fixture --task pass --watch

# ABC layout smoke: --layout=auto picks abc/<num>/<letter>.py for abc<NNN> contest IDs.
run_case "abc999/a test (--layout auto)"    0 test abc999 --task a
run_case "abc999/a test (--layout abc)"     0 test abc999 --task a --layout abc

# `exercise new abc` (contest prepare) smoke, offline via --no-fetch so no network.
# abc998 has no pre-populated cache; --no-fetch + --tasks builds a minimal contest.toml
# and generates empty abc/998/{a,b}.py skeletons.
run_case "new abc abc998 --no-fetch"        0 new abc abc998 --no-fetch --tasks a,b
test -f "$STAGE/abc/998/a.py" && test -f "$STAGE/abc/998/b.py" \
    || { echo "  ✗ new abc did not create skeletons"; failures=$((failures + 1)); }
test -f "$CACHE_HOME/atcoder-tools/abc998/contest.toml" \
    || { echo "  ✗ new abc did not save contest.toml"; failures=$((failures + 1)); }
# Invalid contest ID is rejected.
run_case "new abc arc100 (bad id)"          1 new abc arc100 --no-fetch --tasks a

# `exercise run` (ad-hoc stdin) smoke tests
INPUT_FILE="$STAGE/run-input.txt"
echo "5" > "$INPUT_FILE"
run_case "run fixture_pass --in"      0 run fixture --task pass --in "$INPUT_FILE"
run_case "run fixture_re   --in"      1 run fixture --task re   --in "$INPUT_FILE"
run_case "run fixture_tle  --in"      1 run fixture --task tle  --in "$INPUT_FILE"

# --out judge: fixture_pass は 5 → 10 を出すので、 expected=10 で PASS、99 で FAIL。
OK_OUT="$STAGE/run-expected-ok.txt"
NG_OUT="$STAGE/run-expected-ng.txt"
echo "10" > "$OK_OUT"
echo "99" > "$NG_OUT"
run_case "run fixture_pass --in --out (PASS)" 0 run fixture --task pass --in "$INPUT_FILE" --out "$OK_OUT"
run_case "run fixture_pass --in --out (FAIL)" 1 run fixture --task pass --in "$INPUT_FILE" --out "$NG_OUT"

# ABC layout: abc999_a is the same N→N*2 program. Test exercise run end-to-end on ABC layout.
run_case "abc999/a run --in --out PASS"       0 run abc999 --task a --in "$INPUT_FILE" --out "$OK_OUT"

# --in - と --in 省略は等価 (どちらも親 stdin を read-all する batch)。
run_piped "run fixture_pass --in - (batch stdin)"  0 "5
" run fixture --task pass --in -
run_piped "run fixture_pass (no --in, batch stdin)" 0 "5
" run fixture --task pass

# Interactive mode: --interactive で親 stdin に直結。piped 入力でも query/response の
# 交互が成立することを確認 (非TTY では passthrough + tee)。
run_piped "run fixture_interactive --interactive"  0 "3
ok
ok
ok
" run fixture --task interactive --interactive

# --interactive は --out / ファイル --in と併用不可 (引数エラー = exit 2)。
run_case "run --interactive + --out (reject)"  2 run fixture --task pass --interactive --out "$OK_OUT"
run_case "run --interactive + file --in (reject)" 2 run fixture --task pass --interactive --in "$INPUT_FILE"

# `exercise submit` smoke: 全テスト通過なら exit 0、未通過なら中止して exit 1。
# --no-open でブラウザは開かないが、通過ケースは OS のクリップボードを書き換える点に注意。
run_case "submit fixture pass --no-open"  0 submit fixture --task pass --no-open
run_case "submit fixture fail --no-open"  1 submit fixture --task fail --no-open

echo
if [[ "$failures" -gt 0 ]]; then
    echo "${failures} case(s) failed"
    exit 1
fi
echo "All fixtures behaved as expected."
