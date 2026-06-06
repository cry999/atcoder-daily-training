#!/usr/bin/env bash
# fixtures/run.sh -- `exercise test` コマンドのスモークテスト
#
# fixtures/ にある fixture を一時ディレクトリ内の `exercise/YYYY/MM/DD/` に複製し、
# そこに `cd` してからツールを呼び出すことで、ツール本体に「テスト用パス上書き」のような
# 機能を持たせずに各種ステータス (PASS/FAIL/RE/TLE/DEBUG) を一周検査する。

set -euo pipefail

cd "$(dirname "$0")/.."
REPO_ROOT="$(pwd)"
FIXTURES="$REPO_ROOT/fixtures"

# Build the tool.
TOOL_DIR="$(mktemp -d)"
trap 'rm -rf "$TOOL_DIR" "$STAGE"' EXIT
BIN="$TOOL_DIR/exercise"
echo "Building $BIN ..."
go build -o "$BIN" ./cmd/exercise

# Stage fixtures under <stage>/exercise/YYYY/MM/DD/, then cd there.
STAGE="$(mktemp -d)"
DATE_DIR="exercise/$(date +%Y/%m/%d)"
mkdir -p "$STAGE/$DATE_DIR"
cp -R "$FIXTURES/"fixture_* "$STAGE/$DATE_DIR/"

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

run_case "fixture_pass"          0 test fixture --task pass
run_case "fixture_fail"          1 test fixture --task fail
run_case "fixture_re"            1 test fixture --task re
run_case "fixture_tle"           1 test fixture --task tle
run_case "fixture_debug w/o -d"  1 test fixture --task debug
run_case "fixture_debug w/  -d"  0 test fixture --task debug -d

echo
if [[ "$failures" -gt 0 ]]; then
    echo "${failures} case(s) failed"
    exit 1
fi
echo "All fixtures behaved as expected."
