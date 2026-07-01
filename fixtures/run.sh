#!/usr/bin/env bash
# fixtures/run.sh -- `atcoder test` / `atcoder run` のスモークテスト
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
trap 'rm -rf "$TOOL_DIR" "$STAGE" "$CACHE_HOME" "$CONFIG_HOME" "$DATA_HOME"' EXIT
BIN="$TOOL_DIR/atcoder"
echo "Building $BIN ..."
go build -o "$BIN" ./cmd/atcoder

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

# Isolate XDG_CONFIG_HOME to an empty dir so the smoke tests never pick up a real
# ~/.config/atcoder-daily-training/config.toml. Config-specific tests below point
# XDG_CONFIG_HOME at their own staged config.
CONFIG_HOME="$(mktemp -d)"
export XDG_CONFIG_HOME="$CONFIG_HOME"

# Isolate XDG_DATA_HOME so usage telemetry (要件 037) records into a throwaway dir,
# never the real ~/.local/share/atcoder-tools/usage/events.jsonl. The recording hook
# runs for every invocation below; this keeps it self-contained and cleaned up.
DATA_HOME="$(mktemp -d)"
export XDG_DATA_HOME="$DATA_HOME"

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

# check_output は exit code に加えて stdout/stderr の grep 一致も検査する。
# (側 (side_by_side) や --json 本文のように、exit code を変えない出力を検証する用途。)
# check_output <label> <expected_exit> <has|hasnot> <pattern> -- <args...>
check_output() {
    local label="$1" expected_exit="$2" mode="$3" pattern="$4"
    shift 5 # label exit mode pattern "--"
    echo
    echo "=== ${label} (expecting exit ${expected_exit}, ${mode} '${pattern}') ==="
    set +e
    local out; out="$("$BIN" "$@" 2>&1)"; local got=$?
    set -e
    echo "$out"
    local ok=1
    [[ "$got" -eq "$expected_exit" ]] || { echo "  ✗ exit ${got} (expected ${expected_exit})"; ok=0; }
    if [[ "$mode" == "has" ]]; then
        echo "$out" | grep -q "$pattern" || { echo "  ✗ output missing '${pattern}'"; ok=0; }
    else
        echo "$out" | grep -q "$pattern" && { echo "  ✗ output unexpectedly has '${pattern}'"; ok=0; }
    fi
    if [[ "$ok" -eq 1 ]]; then echo "  ✓ ok"; else failures=$((failures + 1)); fi
}

run_case "fixture_pass"               0 test fixture --task pass
# 引数順序の非依存 (internal/cliargs): 位置引数 (contest) とフラグを任意順で打てる。
# いずれも `test fixture --task pass` と等価で exit 0。
run_case "order: flag-first"          0 test --task pass fixture
run_case "order: --task=pass first"   0 test --task=pass fixture
run_case "order: contest between"     0 test --task pass fixture -v
run_case "order: -c value then pos"   0 test --task multi -c 02 fixture
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
# tests-extra (ユーザ追加ケース) は公式サンプルの後ろに連結して走る。表示 id は x01/x02。
# fixture_extra: 公式 01 (5→10 PASS) + 追加 x01 (7→14 PASS) + 追加 x02 (3→6 ≠999 FAIL)。
run_case "fixture_extra (extra x02 fails)" 1 test fixture --task extra
run_case "fixture_extra -c x01 (extra pass)" 0 test fixture --task extra -c x01
run_case "fixture_extra -c 01 (official only)" 0 test fixture --task extra -c 01

# --json (要件 042): サンプル判定結果を JSON で stdout に出す。exit code は通常の
# test と同じ (全通過=0 / 不通過=1)。JSON は非 TTY でも出せる (機械向け出力)。
run_case "test --json (pass → exit 0)" 0 test fixture --task pass --json
run_case "test --json (fail → exit 1)" 1 test fixture --task fail --json
# JSON 本文の最低限の妥当性: 全通過なら all_passed=true と status AC を含む。
check_output "test --json body (pass)" 0 has '"all_passed": true' -- test fixture --task pass --json
check_output "test --json body (status AC)" 0 has '"status": "AC"' -- test fixture --task pass --json
# 不通過でも JSON は正常に出る (FAIL は実行エラーではない): all_passed=false。
check_output "test --json body (fail still emits JSON)" 1 has '"all_passed": false' -- test fixture --task fail --json
# --json はサンプル判定モード専用。ad-hoc/対話・watch・submit との併用はフラグ誤り (exit 2)。
run_case "test --json + --interactive (reject)" 2 test fixture --task pass --json --interactive
run_case "test --json + --watch (reject)"       2 test fixture --task pass --json --watch
run_case "test --json + --submit (reject)"      2 test fixture --task pass --json --submit
run_case "test --json + --in (reject)"          2 test fixture --task pass --json --in -

# --submit の提出前チェック + 確認 (要件 044): リスク (不通過・実行不可・DEBUG 検出) が
# あれば確認プロンプトを出すが、run.sh は非 TTY なので stdin の確認は自動で「いいえ」と
# なり提出準備せず exit 1 になる (クリップボード/ブラウザには触れない)。クリーンな
# --submit はコピーの副作用があるため --no-open でブラウザ起動だけ抑止して回す。
run_case "submit on fail (not clean → non-TTY abort)"    1 test fixture --task fail --submit
# fixture_debug: 無条件 [DEBUG] print で生実行は FAIL するが、--submit はコメントアウト後
# ソースを実行する (要件 049) ので [DEBUG] print が消えて PASS → クリーン → 提出準備へ進む。
run_case "submit on debug (commented out → clean → prep)" 0 test fixture --task debug --submit --no-open
# fixture_okdebug: stdout は通過するが sys.stderr.write で [DEBUG] を吐く (= debugstrip の
# regex に拾われずコメントアウトをすり抜ける)。通常実行は PASS、--submit はコメントアウト
# 後ソースを実行しても [DEBUG] が残るので検出 → 確認 → 非 TTY 中止 (要件 049 の安全網)。
run_case "fixture_okdebug (stderr debug, stdout ok)"     0 test fixture --task okdebug
run_case "submit on okdebug (debug survives comment-out → abort)" 1 test fixture --task okdebug --submit
check_output "submit abort prints precheck reasons" 1 has '提出前チェック' -- test fixture --task okdebug --submit

# watch モードは TTY 必須。run.sh の出力は非 TTY なので --watch は exit 2 で拒否される。
# (watch ループ本体は常駐してブロックするため、ここでは回さない。)
run_case "fixture_pass --watch (non-TTY reject)" 2 test fixture --task pass --watch

# start は解答ファイルを用意してから watch を起動する。run.sh は非 TTY なので watch
# 段階で exit 2 になるが、その前に解答ファイルが作られることを確認する (start 固有部分)。
# --until-pass の「全通過で終了」は TTY 必須のため run.sh では扱わない (手動確認)。
run_case "start creates skeleton then rejects non-TTY" 2 start fixture --task brandnew
test -f "$STAGE/$DATE_DIR/fixture_brandnew.py" \
    && echo "  ✓ start created exercise/.../fixture_brandnew.py" \
    || { echo "  ✗ start did not create the skeleton file"; failures=$((failures + 1)); }
run_case "start without --task (reject)" 2 start fixture

# ----- meta コマンド (要件 046) -----
# fetch はネットワークに触れるため run.sh では回さない。プリポピュレートされた
# fixture キャッシュ (書き込み可能な temp XDG_CACHE_HOME にコピー済み) に対して
# show / set と、引数誤り (exit 2) / 未キャッシュ (exit 1) を固定する。
run_case "meta show (contest+task)"          0 meta show fixture --task pass
run_case "meta show (task URL)"              0 meta show https://atcoder.jp/contests/fixture/tasks/fixture_pass
run_case "meta set --time-limit"             0 meta set fixture --task pass --time-limit 5s
run_case "meta set via task URL"             0 meta set https://atcoder.jp/contests/fixture/tasks/fixture_pass --time-limit 3s
run_case "meta show (uncached → exit 1)"     1 meta show fixture --task nope
run_case "meta set (uncached → exit 1)"      1 meta set fixture --task nope --time-limit 5s
# url override: 未キャッシュのスロットにも記録できる (空 meta を作る)。実際の取得は
# ネットワークに触れるため回さず、set の成功と show が記録した url を読めることを固定する。
run_case "meta set --url on uncached slot"   0 meta set fixture --task urltest --url https://atcoder.jp/contests/fixture/tasks/other_x
run_case "meta show (url-only slot, not fetched)" 0 meta show fixture --task urltest
run_case "meta set --url (bad url → exit 2)" 2 meta set fixture --task pass --url not-a-url
run_case "meta (no subcommand → exit 2)"     2 meta
run_case "meta bogus (unknown sub → exit 2)" 2 meta bogus
run_case "meta fetch (no target → exit 2)"   2 meta fetch
run_case "meta show (no --task/URL → exit 2)" 2 meta show fixture
run_case "meta set (no fields → exit 2)"     2 meta set fixture --task pass
run_case "meta set (bad duration → exit 2)"  2 meta set fixture --task pass --time-limit nope
run_case "meta set (zero duration → exit 2)" 2 meta set fixture --task pass --time-limit 0s
run_case "meta show (bad URL → exit 2)"      2 meta show https://atcoder.jp/contests/fixture

# ----- ユーザ設定ファイル (config.toml) -----
# config の側 (side_by_side) は終了コードを変えないので、出力に diff の
# side-by-side ラベルが出るか/出ないかで検証する (check_output は冒頭で定義済み)。

# config を置く専用の XDG_CONFIG_HOME を用意する。
CFG_DIR="$(mktemp -d)"
mkdir -p "$CFG_DIR/atcoder-daily-training"
printf '[test]\nside_by_side = true\n' > "$CFG_DIR/atcoder-daily-training/config.toml"

# config で side_by_side=true → -s 省略でも side-by-side diff になる (FAIL = exit 1)。
XDG_CONFIG_HOME="$CFG_DIR" check_output "config side_by_side=true → side-by-side diff" \
    1 has "side-by-side" -- test fixture --task diff
# 明示 --side-by-side=false は config の true を上書きして unified に戻す。
XDG_CONFIG_HOME="$CFG_DIR" check_output "flag --side-by-side=false overrides config" \
    1 hasnot "side-by-side" -- test fixture --task diff --side-by-side=false

# 壊れた config.toml はパース失敗で exit 2。
BAD_CFG_DIR="$(mktemp -d)"
mkdir -p "$BAD_CFG_DIR/atcoder-daily-training"
printf '[test]\nside_by_side = \n' > "$BAD_CFG_DIR/atcoder-daily-training/config.toml"
XDG_CONFIG_HOME="$BAD_CFG_DIR" run_case "malformed config.toml (parse error)" \
    2 test fixture --task pass
rm -rf "$CFG_DIR" "$BAD_CFG_DIR"
# bash では関数呼び出し前置の代入が残存しうるので、隔離用の空 config dir に戻す。
export XDG_CONFIG_HOME="$CONFIG_HOME"

# ----- config サブコマンド (show / get / set / path) -----
# 空 config では show が既定値を出す。layout 未設定は auto に見える (実効既定値)。
check_output "config show (default)"   0 has   "side_by_side = false" -- config show
check_output "config show layout=auto" 0 has   "layout = auto"        -- config show
check_output "config get layout (default auto)" 0 has "auto"          -- config get layout
# path は config.toml の所在を出す。
check_output "config path"             0 has   "config.toml"          -- config path
# 未知サブコマンド / キー / 型不一致 / 引数不足は exit 2。
run_case    "config (no subcommand)"        2 config
run_case    "config bogus (unknown sub)"    2 config bogus
run_case    "config get unknown key"        2 config get bogus.key
run_case    "config set unknown key"        2 config set bogus.key x
run_case    "config set invalid bool value" 2 config set test.side_by_side notabool
run_case    "config set invalid layout value" 2 config set layout junk
run_case    "config get (missing key arg)"  2 config get
run_case    "config set (missing value)"    2 config set test.side_by_side

# 書き込み専用 dir で set → get の往復、および set した値が test に波及することを確認。
CFGW="$(mktemp -d)"
XDG_CONFIG_HOME="$CFGW" run_case     "config set test.side_by_side true"  0 config set test.side_by_side true
XDG_CONFIG_HOME="$CFGW" check_output "config get reads back the set value" 0 has "true" -- config get test.side_by_side
XDG_CONFIG_HOME="$CFGW" check_output "config set propagates to test"       1 has "side-by-side" -- test fixture --task diff
XDG_CONFIG_HOME="$CFGW" run_case     "config set layout abc"              0 config set layout abc
XDG_CONFIG_HOME="$CFGW" check_output "config get layout reads back abc"   0 has "abc" -- config get layout
rm -rf "$CFGW"
export XDG_CONFIG_HOME="$CONFIG_HOME"

# ----- config alias (git 風) -----
# [alias] に置いた名前で atcoder <name> が展開される。組み込み優先・ループ検出・unset を確認。
ALIASCFG="$(mktemp -d)"
XDG_CONFIG_HOME="$ALIASCFG" run_case "config set alias.v = version"        0 config set alias.v version
# atcoder v → version (組み込み・オフライン)。展開が効いていれば exit 0。
XDG_CONFIG_HOME="$ALIASCFG" run_case "alias v expands to version"          0 v
XDG_CONFIG_HOME="$ALIASCFG" check_output "config get alias.v"             0 has "version" -- config get alias.v
XDG_CONFIG_HOME="$ALIASCFG" check_output "config show lists alias.v"      0 has "alias.v = version" -- config show
XDG_CONFIG_HOME="$ALIASCFG" run_case "config unset alias.v"               0 config unset alias.v
XDG_CONFIG_HOME="$ALIASCFG" run_case "config unset alias.nope (undefined)" 2 config unset alias.nope
XDG_CONFIG_HOME="$ALIASCFG" run_case "config set alias.<bad name> reject"  2 config set "alias.bad name" version
# 組み込み名の alias は保存できる (警告 stderr) が dispatch では無視される。
XDG_CONFIG_HOME="$ALIASCFG" run_case "config set alias.test (warns, exit 0)" 0 config set alias.test version
rm -rf "$ALIASCFG"
# alias ループ (a→b→a) は exit 2。
ALIASLOOP="$(mktemp -d)"
mkdir -p "$ALIASLOOP/atcoder-daily-training"
printf '[alias]\na = "b"\nb = "a"\n' > "$ALIASLOOP/atcoder-daily-training/config.toml"
XDG_CONFIG_HOME="$ALIASLOOP" run_case "alias loop (exit 2)"                2 a
rm -rf "$ALIASLOOP"
export XDG_CONFIG_HOME="$CONFIG_HOME"

# ABC layout smoke: --layout=auto picks abc/<num>/<letter>.py for abc<NNN> contest IDs.
run_case "abc999/a test (--layout auto)"    0 test abc999 --task a
run_case "abc999/a test (--layout abc)"     0 test abc999 --task a --layout abc

# ----- 既定レイアウトの解決順 (--layout > $ATCODER_LAYOUT > config layout > auto) -----
# 不正な layout 値はどの出所でも layout.Resolve が Parse 前に弾いて exit 2。
# precedence は「上位が valid なら下位の不正値は評価されない (=exit 0)」で検証する。
# (abc999 は cache 済みで abc/999/a.py = n→n*2 が PASS する。)
LAYCFG="$(mktemp -d)"; mkdir -p "$LAYCFG/atcoder-daily-training"
printf 'layout = "junk"\n' > "$LAYCFG/atcoder-daily-training/config.toml"
# flag/env 未指定なら config 層が読まれ、不正値で exit 2。
XDG_CONFIG_HOME="$LAYCFG" run_case "config layout=junk → resolve error"   2 test abc999 --task a
# env が config より優先: env=abc なら config の junk は評価されず PASS。
XDG_CONFIG_HOME="$LAYCFG" ATCODER_LAYOUT=abc run_case "env abc beats config junk" 0 test abc999 --task a
unset ATCODER_LAYOUT
export XDG_CONFIG_HOME="$CONFIG_HOME"
# env 単体の不正値も exit 2。
ATCODER_LAYOUT=junk run_case "env layout=junk → resolve error"           2 test abc999 --task a
# flag が env より優先: flag=abc なら env の junk は評価されず PASS。
ATCODER_LAYOUT=junk run_case "flag abc beats env junk"                   0 test abc999 --task a --layout abc
unset ATCODER_LAYOUT
rm -rf "$LAYCFG"

# `atcoder new abc` (contest prepare) smoke, offline via --no-fetch so no network.
# abc998 has no pre-populated cache; --no-fetch + --tasks builds a minimal contest.toml
# and generates empty abc/998/{a,b}.py skeletons.
run_case "new abc abc998 --no-fetch"        0 new abc abc998 --no-fetch --tasks a,b
test -f "$STAGE/abc/998/a.py" && test -f "$STAGE/abc/998/b.py" \
    || { echo "  ✗ new abc did not create skeletons"; failures=$((failures + 1)); }
test -f "$CACHE_HOME/atcoder-tools/abc998/contest.toml" \
    || { echo "  ✗ new abc did not save contest.toml"; failures=$((failures + 1)); }
# Invalid contest ID is rejected.
run_case "new abc arc100 (bad id)"          1 new abc arc100 --no-fetch --tasks a

# ----- gen コマンド (要件 060): 制約・入力形式からランダム入力を生成 -----
# fetch はネットワークに触れるため回さない。プリポピュレートされた gen.toml
# (fixture/fixture_gen/gen.toml、小さい制約) を解析して生成する経路だけを固定する。
# 生成は乱数だが exit code と --show-spec / --seed の決定性を検査する。
run_case "gen --show-spec"                   0 gen fixture --task gen --show-spec
run_case "gen (stdout, seeded)"              0 gen fixture --task gen --seed 1
run_case "gen --size max (seeded)"           0 gen fixture --task gen --size max --seed 1
run_case "gen --size min (seeded)"           0 gen fixture --task gen --size min --seed 1
# --show-spec は認識できた形式・変数・カバレッジを出す (この fixture は full)。
check_output "gen --show-spec shows format"  0 has "scalar : N M"  -- gen fixture --task gen --show-spec
check_output "gen --show-spec coverage full" 0 has "coverage: full" -- gen fixture --task gen --show-spec
# -n 2 -o <dir>: 2 件を <dir>/01.in, 02.in に書く。
GENDIR="$STAGE/gen-out"
run_case "gen -n 2 -o <dir>"                 0 gen fixture --task gen -n 2 -o "$GENDIR" --seed 3
test -f "$GENDIR/01.in" && test -f "$GENDIR/02.in" \
    || { echo "  ✗ gen -n 2 did not write NN.in files"; failures=$((failures + 1)); }
# --save: 生成入力を tests-extra に入力のみケース (空 .out) で追加する。
run_case "gen --save (input-only case)"      0 gen fixture --task gen --save --seed 4
test -f "$CACHE_HOME/atcoder-tools/fixture/fixture_gen/tests-extra/01.in" \
    || { echo "  ✗ gen --save did not add a tests-extra case"; failures=$((failures + 1)); }
# 引数・フラグ誤り = exit 2。
run_case "gen without --task (reject)"       2 gen fixture
run_case "gen --show-spec + --seed (reject)" 2 gen fixture --task gen --show-spec --seed 1
run_case "gen --size huge (reject)"          2 gen fixture --task gen --size huge

# ad-hoc モード (旧 run): `atcoder test --in/--out/--interactive` で 1 件実行。
INPUT_FILE="$STAGE/run-input.txt"
echo "5" > "$INPUT_FILE"
run_case "test --in (ad-hoc OK)"      0 test fixture --task pass --in "$INPUT_FILE"
run_case "test --in (ad-hoc RE)"      1 test fixture --task re   --in "$INPUT_FILE"
run_case "test --in (ad-hoc TLE)"     1 test fixture --task tle  --in "$INPUT_FILE"

# --out judge: fixture_pass は 5 → 10 を出すので、 expected=10 で PASS、99 で FAIL。
OK_OUT="$STAGE/run-expected-ok.txt"
NG_OUT="$STAGE/run-expected-ng.txt"
echo "10" > "$OK_OUT"
echo "99" > "$NG_OUT"
run_case "test --in --out (PASS)" 0 test fixture --task pass --in "$INPUT_FILE" --out "$OK_OUT"
run_case "test --in --out (FAIL)" 1 test fixture --task pass --in "$INPUT_FILE" --out "$NG_OUT"

# ABC layout: abc999_a is the same N→N*2 program. ad-hoc を ABC レイアウトで end-to-end。
run_case "abc999/a test --in --out PASS"      0 test abc999 --task a --in "$INPUT_FILE" --out "$OK_OUT"

# stdin から ad-hoc は `--in -` を明示する (統一後の仕様)。
run_piped "test --in - (ad-hoc stdin)"  0 "5
" test fixture --task pass --in -

# ad-hoc フラグ無しなら、stdin がパイプされていても既定のサンプル判定 (stdin 無視)。
run_piped "test no ad-hoc flags ignores stdin -> samples" 0 "5
" test fixture --task pass

# サンプル専用フラグ (-c 等) と ad-hoc フラグの併用は exit 2 (モード混在)。
run_case "test --in + -c (mode mix reject)" 2 test fixture --task pass --in "$INPUT_FILE" -c 01

# --keep-debug は --submit (サンプルモード) 専用。ad-hoc フラグとの併用は exit 2。
run_case "test --in + --keep-debug (mode mix reject)" 2 test fixture --task pass --in "$INPUT_FILE" --keep-debug

# Interactive mode: --interactive で親 stdin に直結。piped 入力でも query/response の
# 交互が成立することを確認 (非TTY では passthrough + tee)。
run_piped "test --interactive (non-TTY passthrough)"  0 "3
ok
ok
ok
" test fixture --task interactive --interactive

# --interactive は --out / ファイル --in と併用不可 (引数エラー = exit 2)。
run_case "test --interactive + --out (reject)"  2 test fixture --task pass --interactive --out "$OK_OUT"
run_case "test --interactive + file --in (reject)" 2 test fixture --task pass --interactive --in "$INPUT_FILE"

# --auto-restart (-R): 対話モードの chat TUI を sticky auto-restart にする起動フラグ。
# 非 TTY では chat TUI を使わず passthrough で 1 回実行するだけ (フラグは無効・exit 0)。
run_piped "test --interactive --auto-restart (non-TTY no-op)"  0 "3
ok
ok
ok
" test fixture --task interactive --interactive --auto-restart
run_piped "test -I -R (short forms)"  0 "3
ok
ok
ok
" test fixture --task interactive -I -R
# --auto-restart は --interactive 必須。単体指定はフラグ誤り = exit 2。
run_case "test --auto-restart without --interactive (reject)" 2 test fixture --task pass --auto-restart

# 旧 `run` サブコマンドは削除済み → 未知サブコマンドで exit 2。
run_case "run subcommand removed" 2 run fixture --task pass

# 提出準備 (旧 submit) は `test --submit` に畳んだ。全通過なら exit 0、未通過なら
# 提出準備せず exit 1。--no-open でブラウザは開かないが、通過ケースは OS の
# クリップボードを書き換える点に注意。
run_case "test --submit (pass)"  0 test fixture --task pass --submit --no-open
run_case "test --submit (fail)"  1 test fixture --task fail --submit --no-open
# --submit はサンプルモード専用 → ad-hoc / watch との併用は exit 2。
run_case "test --submit + --in (reject)" 2 test fixture --task pass --submit --no-open --in "$INPUT_FILE"
run_case "test --submit + --watch (reject)" 2 test fixture --task pass --submit -w
# 旧 `submit` サブコマンドは削除済み → 未知サブコマンドで exit 2。
run_case "submit subcommand removed" 2 submit fixture --task pass

# `atcoder stats` smoke: exercise/ ツリーを集計する読み取り専用コマンド。
# STAGE には当日 dir の fixture_*.py が居るので集計対象がある。過去日も足して
# 複数日・週別時系列の経路を踏ませる。期間フラグ排他違反は exit 2。
mkdir -p "$STAGE/exercise/2026/05/20" "$STAGE/exercise/2026/06/01"
cp "$FIXTURES/fixture_pass.py" "$STAGE/exercise/2026/05/20/abc457_d.py"
cp "$FIXTURES/fixture_pass.py" "$STAGE/exercise/2026/06/01/arc180_c.py"
run_case "stats (all time)"            0 stats
run_case "stats --month"               0 stats --month
run_case "stats --week"                0 stats --week
run_case "stats --year"                0 stats --year
run_case "stats --week --month reject" 2 stats --week --month
# 短縮形 -w/-m/-y は長形と同一フラグ。混在指定も排他違反 (exit 2)。
run_case "stats -w"                    0 stats -w
run_case "stats -m"                    0 stats -m
run_case "stats -y"                    0 stats -y
run_case "stats -w --month reject"     2 stats -w --month
# ローリング期間 --last <dur>: 今日から N 単位分。短縮形 -l。bare d/w/m/y は 1 扱い。
run_case "stats --last 7d"             0 stats --last 7d
run_case "stats --last 1m"             0 stats --last 1m
run_case "stats --last 1y"             0 stats --last 1y
run_case "stats -l m (bare unit)"      0 stats -l m
run_case "stats --last 0d reject"      2 stats --last 0d
run_case "stats --last 1x reject"      2 stats --last 1x
run_case "stats --week --last 7d rej"  2 stats --week --last 7d
# --graph (-g): 時系列を草グリッドで表示。期間フラグ/--last と併用可。排他は維持。
run_case "stats --graph"               0 stats --graph
run_case "stats -g"                    0 stats -g
run_case "stats --year --graph"        0 stats --year --graph
run_case "stats -m -g"                 0 stats -m -g
run_case "stats --last 2w -g"          0 stats --last 2w -g
run_case "stats -g -w --month reject"  2 stats -g -w --month

# `atcoder review <category>` smoke: exercise ツリー (abc457_d, 日付あり) と
# カテゴリツリー abc/999/a.py (日付なし) を横断してコンテスト単位で列挙する。
# 非 TTY (run.sh の出力) では一括テキスト出力を踏む。カテゴリは必須の位置引数。
run_case "review abc"                  0 review abc
run_case "review arc"                  0 review arc
run_case "review abc --month"          0 review abc --month
run_case "review abc -l 2w"            0 review abc -l 2w
run_case "review xyz (0 件・成功)"      0 review xyz
run_case "review (no category) reject" 2 review
run_case "review abc -w --month rej"   2 review abc -w --month
run_case "review abc --last 0d reject" 2 review abc --last 0d
# 横断の中身: abc/999 (カテゴリツリー由来・日付なし) が出て last solved が "—" になる。
# (全期間なら現在日に依存せず常に含まれる。)
check_output "review reads abc/ category tree" 0 has "abc999" -- review abc
check_output "review undated row shows dash"   0 has "—"      -- review abc
# 期間フィルタ (--year) では日付なしの abc/999 は必ず落ちる (時刻に依存しない不変則)。
check_output "review --year drops undated abc999" 0 hasnot "abc999" -- review abc --year


# `atcoder completion` smoke: 各シェルのスクリプト出力と、隠し __complete ヘルパ。
# completion の引数エラーは exit 2。__complete は常に exit 0 で候補を吐く。
run_case "completion bash"               0 completion bash
run_case "completion zsh"                0 completion zsh
run_case "completion fish"               0 completion fish
run_case "completion (no shell)"         2 completion
run_case "completion powershell (bad)"   2 completion powershell
run_case "__complete (always exit 0)"    0 __complete -- te
# 候補内容を検証 (キャッシュ/cwd 非依存な静的・既定候補のみ)。出力は "値<TAB>説明"
# 形式なので、値の一致は 1 列目 (cut -f1) で見る。
"$BIN" __complete -- te | cut -f1 | grep -qx "test" \
    || { echo "  ✗ __complete -- te did not yield 'test'"; failures=$((failures + 1)); }
"$BIN" __complete -- "" | cut -f1 | grep -qx "completion" \
    || { echo "  ✗ __complete -- '' missing 'completion'"; failures=$((failures + 1)); }
"$BIN" __complete -- test abc999 --layout "" | cut -f1 | grep -qx "abc" \
    || { echo "  ✗ __complete --layout did not yield 'abc'"; failures=$((failures + 1)); }
# config の layout キーは値補完 (enum) を持つ: `config set layout <TAB>` → abc/auto/exercise。
"$BIN" __complete -- config set layout "" | cut -f1 | grep -qx "exercise" \
    || { echo "  ✗ __complete config set layout did not yield 'exercise'"; failures=$((failures + 1)); }
# config の既知キー補完に layout が出る。
"$BIN" __complete -- config get "" | cut -f1 | grep -qx "layout" \
    || { echo "  ✗ __complete config get did not yield 'layout'"; failures=$((failures + 1)); }
# abc000 は staging にもキャッシュにも無いので、既定 letter (a〜g) 経路を踏む。
"$BIN" __complete -- test abc000 --task "" | cut -f1 | grep -qx "d" \
    || { echo "  ✗ __complete --task did not yield default letters"; failures=$((failures + 1)); }
# 静的候補には説明 (2 列目) が付く。cut -s -f2 はタブの無い行を抑止するので、
# 説明付きなら非空・動的候補 (letter) なら空になる。
[[ -n "$("$BIN" __complete -- te | cut -s -f2)" ]] \
    || { echo "  ✗ __complete -- te missing description column"; failures=$((failures + 1)); }
[[ -z "$("$BIN" __complete -- test abc000 --task "" | cut -s -f2)" ]] \
    || { echo "  ✗ __complete --task letters should have no description"; failures=$((failures + 1)); }

# `atcoder version` / `atcoder update`: 自己更新。version はオフラインで動き常に exit 0。
# update の引数誤りは exit 2。ネットワーク経路 (最新解決・install) は run.sh では叩かず、
# 最新解決が決定的に失敗する経路 (exit 1) だけ固定する。update は自モジュールを
# GOPRIVATE に入れて proxy をバイパスするので、GOPROXY=off だけでは止まらない。
# GONOPROXY=none で「どのモジュールも proxy をバイパスしない」を強制し、off の proxy に
# 確実に当てて失敗させる。
run_case "version (offline)"             0 version
run_case "update --bogus (reject)"       2 update --bogus
GOPROXY=off GONOPROXY=none run_case "update --check (proxy off → exit 1)" 1 update --check
# --local は cwd の ./cmd/atcoder を入れる。--check との併用は排他で exit 2。
# STAGE は module 外なので素の --local は go install が失敗して exit 1
# (実際の GOBIN を汚さないよう throwaway を渡す)。
run_case "update --local --check (reject)" 2 update --local --check
GOBIN="$(mktemp -d)" run_case "update --local outside a module (exit 1)" 1 update --local

# zsh 補完の regression: 補完中の空トークン (何も入力していない位置) を __complete に
# 渡せているか。旧 `${words[2,$CURRENT]}` (unquoted) は空要素を落とし、位置を誤判定して
#   - サブコマンドの次の位置引数 → サブコマンドを候補に (例 `atcoder test <TAB>`)
#   - フラグ指定後 → 直前と同じフラグを再提案 (例 `atcoder test --refresh <TAB>`)
# してしまっていた。修正は `"${(@)words[2,$CURRENT]}"` で空要素を保持すること。
# zsh の _atcoder を stub した compadd/_describe で駆動し、出した候補 (値のみ) を表示する。
zsh_cands_for() {
    BIN="$BIN" zsh -c '
        compdef(){ : }
        compadd(){ while (( $# )); do [[ $1 == "--" ]] && { shift; break }; [[ $1 == -* ]] || break; shift; done; print -rl -- "$@" }
        _describe(){ shift; local -a a; eval "a=(\"\${${1}[@]}\")"; print -rl -- "${a[@]%%:*}" }
        source <($BIN completion zsh)
        '"$1"'
        _atcoder
    ' 2>/dev/null || true
}
# 利用テレメトリ (要件 037): 上の各ケースが XDG_DATA_HOME に記録されているはず。
# usage はオフライン・読み取り専用で集計を出す (exit 0)。--flags 内訳も exit 0。
run_case "usage (offline aggregate)" 0 usage
run_case "usage --flags" 0 usage --flags
run_case "usage --json" 0 usage --json

echo
echo "=== usage telemetry: events were recorded; ATCODER_NO_USAGE disables it ==="
EVENTS="$DATA_HOME/atcoder-tools/usage/events.jsonl"
if [[ -s "$EVENTS" ]] && grep -q '"cmd":"test"' "$EVENTS"; then
    echo "  ✓ events.jsonl recorded test invocations"
else
    echo "  ✗ expected recorded 'test' events in $EVENTS"; failures=$((failures + 1))
fi
# ATCODER_NO_USAGE=1 で記録しないこと (新しい DATA_HOME に切り替えて検証)。
NOUSE_HOME="$(mktemp -d)"
XDG_DATA_HOME="$NOUSE_HOME" ATCODER_NO_USAGE=1 "$BIN" version >/dev/null 2>&1 || true
if [[ -e "$NOUSE_HOME/atcoder-tools/usage/events.jsonl" ]]; then
    echo "  ✗ ATCODER_NO_USAGE=1 must not write the usage log"; failures=$((failures + 1))
else
    echo "  ✓ ATCODER_NO_USAGE=1 suppressed recording"
fi
rm -rf "$NOUSE_HOME"

echo
echo "=== zsh completion: empty current word must not offer subcommands / repeat flags ==="
if command -v zsh >/dev/null 2>&1; then
    sub_re="new|test|stats|config|commit|completion|update|version|review"
    # (1) `atcoder test <TAB>` (位置引数) はサブコマンドを出してはいけない。
    pos=$(zsh_cands_for 'words=(atcoder test ""); CURRENT=3')
    # (2) `atcoder test --refresh <TAB>` は --refresh を再提案してはいけない。
    flag=$(zsh_cands_for 'words=(atcoder test --refresh ""); CURRENT=4')
    if printf "%s\n" "$pos" | grep -qxE "$sub_re"; then
        echo "  ✗ subcommand offered at the <contest> position (empty current dropped)"; failures=$((failures + 1))
    elif printf "%s\n" "$flag" | grep -qxE "\-\-refresh"; then
        echo "  ✗ flag --refresh re-offered after it was already given (empty current dropped)"; failures=$((failures + 1))
    else
        echo "  ✓ positional → $(printf "%s " $pos | head -c 30); after --refresh → $(printf "%s " $flag | head -c 30)"
    fi
else
    echo "  (zsh not installed; skipping)"
fi

echo
if [[ "$failures" -gt 0 ]]; then
    echo "${failures} case(s) failed"
    exit 1
fi
echo "All fixtures behaved as expected."
