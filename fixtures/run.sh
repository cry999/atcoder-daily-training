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
trap 'rm -rf "$TOOL_DIR" "$STAGE" "$CACHE_HOME" "$CONFIG_HOME"' EXIT
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

# ----- ユーザ設定ファイル (config.toml) -----
# config の側 (side_by_side) は終了コードを変えないので、出力に diff の
# side-by-side ラベルが出るか/出ないかで検証する。
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
# 空 config では show が既定値を出す。
check_output "config show (default)"   0 has   "side_by_side = false" -- config show
# path は config.toml の所在を出す。
check_output "config path"             0 has   "config.toml"          -- config path
# 未知サブコマンド / キー / 型不一致 / 引数不足は exit 2。
run_case    "config (no subcommand)"        2 config
run_case    "config bogus (unknown sub)"    2 config bogus
run_case    "config get unknown key"        2 config get bogus.key
run_case    "config set unknown key"        2 config set bogus.key x
run_case    "config set invalid bool value" 2 config set test.side_by_side notabool
run_case    "config get (missing key arg)"  2 config get
run_case    "config set (missing value)"    2 config set test.side_by_side

# 書き込み専用 dir で set → get の往復、および set した値が test に波及することを確認。
CFGW="$(mktemp -d)"
XDG_CONFIG_HOME="$CFGW" run_case     "config set test.side_by_side true"  0 config set test.side_by_side true
XDG_CONFIG_HOME="$CFGW" check_output "config get reads back the set value" 0 has "true" -- config get test.side_by_side
XDG_CONFIG_HOME="$CFGW" check_output "config set propagates to test"       1 has "side-by-side" -- test fixture --task diff
rm -rf "$CFGW"
export XDG_CONFIG_HOME="$CONFIG_HOME"

# ABC layout smoke: --layout=auto picks abc/<num>/<letter>.py for abc<NNN> contest IDs.
run_case "abc999/a test (--layout auto)"    0 test abc999 --task a
run_case "abc999/a test (--layout abc)"     0 test abc999 --task a --layout abc

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

# `atcoder review <category>` smoke: 上の exercise ツリー (abc457_d, arc180_c) を
# コンテスト単位で列挙する読み取り専用コマンド。カテゴリは必須の位置引数。
run_case "review abc"                  0 review abc
run_case "review arc"                  0 review arc
run_case "review abc --month"          0 review abc --month
run_case "review abc -l 2w"            0 review abc -l 2w
run_case "review xyz (0 件・成功)"      0 review xyz
run_case "review (no category) reject" 2 review
run_case "review abc -w --month rej"   2 review abc -w --month
run_case "review abc --last 0d reject" 2 review abc --last 0d

# `atcoder status` / `login` / `logout` smoke (ネットワーク非依存)。
# XDG_CONFIG_HOME は空隔離 dir なので session.json は存在せず、status は
# LoadSession で「未ログイン」となり exit 1 (HTTP を一切叩かない)。引数誤りは
# exit 2。login は非対話入力経路 (run_piped で非 TTY) を踏ませて検証する。
run_case  "status (not logged in)"            1 status fixture --task pass
run_case  "status (no contest, arg err)"      2 status
run_case  "status --watch w/o --task"         2 status fixture --watch
run_case  "logout (no session, noop)"         0 logout
# login は cookie 取り込み式 (AtCoder ログインは Cloudflare Turnstile 保護のため)。
# 非 TTY かつ --session-cookie/--session-stdin 無し → 対話不可で exit 2。
run_piped "login (non-TTY, no cookie flag)"   2 "" login
# --session-stdin に空入力 → cookie 空で exit 2 (検証ネットワークに到達しない)。
run_piped "login --session-stdin (empty)"     2 "" login --session-stdin

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

# zsh 補完の regression: サブコマンドの次の位置引数 (例 `atcoder test <TAB>`) で、
# 補完中の空トークンが __complete に渡るか。旧 `${words[2,$CURRENT]}` (unquoted) は
# 空要素を落とし、位置をサブコマンド位置と誤判定してサブコマンドを候補にしていた。
# 修正は `"${(@)words[2,$CURRENT]}"` で空要素を保持すること。
echo
echo "=== zsh completion: positional after a subcommand must not offer subcommands ==="
if command -v zsh >/dev/null 2>&1; then
    zsh_cands=$(BIN="$BIN" zsh -c '
        compdef(){ : }
        compadd(){ while (( $# )); do [[ $1 == "--" ]] && { shift; break }; [[ $1 == -* ]] || break; shift; done; print -rl -- "$@" }
        _describe(){ shift; local -a a; eval "a=(\"\${${1}[@]}\")"; print -rl -- "${a[@]%%:*}" }
        source <($BIN completion zsh)
        words=(atcoder test ""); CURRENT=3
        _atcoder
    ' 2>/dev/null) || true
    if printf "%s\n" "$zsh_cands" | grep -qxE "new|test|login|logout|status|stats|config|commit|completion|update|version|review"; then
        echo "  ✗ subcommand offered at the <contest> position (empty current word dropped)"
        failures=$((failures + 1))
    else
        echo "  ✓ no subcommand leak (offered: $(printf "%s " $zsh_cands | head -c 50))"
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
