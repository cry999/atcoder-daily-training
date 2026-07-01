package main

import (
	"bufio"
	"errors"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/cliargs"
	"github.com/cry999/atcoder-daily-training/internal/config"
	"github.com/cry999/atcoder-daily-training/internal/layout"
	"github.com/cry999/atcoder-daily-training/internal/solvestat"
	"golang.org/x/term"
)

// maxDurationMs は実装時間の異常値判定の上限 (12 時間)。日跨ぎ放置などの誤計測を
// 黙って記録しないための閾値 (要件 061)。
const maxDurationMs = int64(12 * 60 * 60 * 1000)

// cmdRecord は記録系サブコマンドの親 dispatch。第 1 引数が start/stop/edit なら
// それぞれへ委譲し、そうでなければ (contest 指定) 記録本体へ入る (要件 061)。
func cmdRecord(args []string) (int, error) {
	if len(args) >= 1 {
		switch args[0] {
		case "start":
			return recordStart(args[1:])
		case "stop":
			return recordStop(args[1:])
		case "edit":
			return 2, errors.New("record edit は未実装です (Phase 2)。今は record の再実行でキー単位訂正できます")
		}
	}
	return recordMain(args)
}

// recordTarget は record 系が解決した対象 (解答パス + category×letter)。
type recordTarget struct {
	path     string
	contest  string
	task     string
	category string
	letter   string
}

// buildRecordTarget は layout を解決し、解答パスと category×letter を求める。
func buildRecordTarget(layoutFlag, contest, task string) (recordTarget, error) {
	lay, err := resolveLayout(layoutFlag, contest)
	if err != nil {
		return recordTarget{}, err
	}
	path, err := lay.SolutionPath(contest, task)
	if err != nil {
		return recordTarget{}, err
	}
	letter, err := layout.Letter(task)
	if err != nil {
		return recordTarget{}, err
	}
	return recordTarget{
		path:     path,
		contest:  contest,
		task:     task,
		category: contestCategory(contest),
		letter:   letter,
	}, nil
}

// targetMs は config の目標実装時間 (category×letter) をミリ秒で返す。未設定なら 0。
func (rt recordTarget) targetMs() int64 {
	cfg, err := config.Load()
	if err != nil {
		return 0
	}
	if d, ok := cfg.TargetDuration(rt.category, rt.letter); ok {
		return d.Milliseconds()
	}
	return 0
}

// contestCategory は contest_id の英字接頭辞を category として返す ("abc457" → "abc")。
func contestCategory(contestID string) string {
	i := 0
	for i < len(contestID) {
		c := contestID[i]
		if (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') {
			i++
			continue
		}
		break
	}
	return strings.ToLower(contestID[:i])
}

// requireTask は --task の必須チェックと短縮形展開を行う。
func requireTask(task, contest string) (string, int, error) {
	if task == "" {
		return "", 2, errors.New("--task is required")
	}
	if !strings.Contains(task, "_") {
		task = contest + "_" + task
	}
	return task, 0, nil
}

// ensureFileExists は path が無ければ親 dir ごと空ファイルを作る (既存は温存)。
func ensureFileExists(path string) error {
	if _, err := os.Stat(path); err == nil {
		return nil
	}
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return err
	}
	return os.WriteFile(path, nil, 0o644)
}

// startedStat は着手時刻だけを持つ Stat を返す (--restart / 新規刻印用)。
func startedStat(now time.Time) solvestat.Stat {
	st := solvestat.Empty()
	st.StartedAt = now
	return st
}

// stampStartedAt は path の解答へ着手時刻を刻む (start / record start 共通)。
//   - restart: 既存ブロックを破棄し started_at=now で置き直す。
//   - solved_at 済み: 完了記録があるので温存 + warning (--restart を案内)。
//   - started_at 済み: 温存 (冪等)。
//   - 未記録: started_at=now を刻む。
//
// stamped は新たに (再)記録したか。破損ブロックは error (呼び出し側で扱う)。
func stampStartedAt(path string, restart bool) (stamped bool, err error) {
	st, found, err := solvestat.ReadFile(path)
	if err != nil {
		return false, err
	}
	now := time.Now()
	if restart {
		if err := solvestat.OverwriteFile(path, startedStat(now)); err != nil {
			return false, err
		}
		return true, nil
	}
	if found && !st.SolvedAt.IsZero() {
		fmt.Fprintln(os.Stderr, "既に完了記録があります。再計測するなら --restart を使ってください。")
		return false, nil
	}
	if found && !st.StartedAt.IsZero() {
		return false, nil // 温存 (冪等)
	}
	if err := solvestat.Update(path, startedStat(now)); err != nil {
		return false, err
	}
	return true, nil
}

// recordStart は計測開始 (着手 UI を伴わない軽量開始)。
func recordStart(args []string) (int, error) {
	flagArgs, positionals := cliargs.Split(args)
	if len(positionals) < 1 {
		return 2, errors.New("contest is required")
	}
	contest := positionals[0]

	fs := flag.NewFlagSet("record start", flag.ContinueOnError)
	taskFlag := addTaskFlag(fs)
	layoutFlag := addLayoutFlag(fs)
	restart := fs.Bool("restart", false, "Reset started_at to now and clear completion (redo practice)")
	fs.SetOutput(os.Stderr)
	if err := fs.Parse(flagArgs); err != nil {
		return 2, err
	}
	task, code, err := requireTask(*taskFlag, contest)
	if err != nil {
		return code, err
	}
	rt, err := buildRecordTarget(*layoutFlag, contest, task)
	if err != nil {
		return 2, err
	}
	if err := ensureFileExists(rt.path); err != nil {
		return 1, err
	}
	stamped, err := stampStartedAt(rt.path, *restart)
	if err != nil {
		return 1, err
	}
	if stamped {
		fmt.Printf("計測を開始しました: %s\n", rt.path)
	} else {
		fmt.Printf("計測は継続中です: %s\n", rt.path)
	}
	return 0, nil
}

// recordStop は計測終端 (スコア対話に入らない最小終端)。
func recordStop(args []string) (int, error) {
	flagArgs, positionals := cliargs.Split(args)
	if len(positionals) < 1 {
		return 2, errors.New("contest is required")
	}
	contest := positionals[0]

	fs := flag.NewFlagSet("record stop", flag.ContinueOnError)
	taskFlag := addTaskFlag(fs)
	layoutFlag := addLayoutFlag(fs)
	acFlag := fs.Bool("ac", false, "Record AC = true")
	noAcFlag := fs.Bool("no-ac", false, "Record AC = false")
	timeFlag := fs.String("time", "", "Override implementation time (e.g. 25m, 1h5m)")
	fs.SetOutput(os.Stderr)
	if err := fs.Parse(flagArgs); err != nil {
		return 2, err
	}
	task, code, err := requireTask(*taskFlag, contest)
	if err != nil {
		return code, err
	}
	ac, err := resolveTriBool(*acFlag, *noAcFlag, "--ac", "--no-ac")
	if err != nil {
		return 2, err
	}
	var overrideMs int64
	if *timeFlag != "" {
		overrideMs, err = parseDurationMs(*timeFlag)
		if err != nil {
			return 2, err
		}
	}
	rt, err := buildRecordTarget(*layoutFlag, contest, task)
	if err != nil {
		return 2, err
	}
	st, _, err := solvestat.ReadFile(rt.path)
	if err != nil {
		if os.IsNotExist(err) {
			return 1, errors.New("解答ファイルがありません。先に atcoder start か atcoder record start してください")
		}
		return 1, err
	}

	now := time.Now()
	patch := solvestat.Empty()
	patch.SolvedAt = now
	durMs := resolveDurationMs(overrideMs, st, now)
	if durMs != 0 {
		durMs = checkAnomaly(durMs)
		patch.DurationMs = durMs
	}
	if tms := rt.targetMs(); tms > 0 {
		patch.TargetMs = tms
	}
	if ac != nil {
		patch.AC = ac
	}
	if err := solvestat.Update(rt.path, patch); err != nil {
		return 1, err
	}
	fmt.Printf("計測を終了しました: %s\n", rt.path)
	printTimeLine(durMs, patch.TargetMs)
	fmt.Println("スコアは `atcoder record " + contest + " --task " + rt.letter + "` で記録できます。")
	return 0, nil
}

// recordMain は記録本体: AC / 解説 / 5 軸を対話 or フラグで埋め、solve-stat へ書き戻す。
func recordMain(args []string) (int, error) {
	flagArgs, positionals := cliargs.Split(args)
	if len(positionals) < 1 {
		return 2, errors.New("contest is required")
	}
	contest := positionals[0]

	fs := flag.NewFlagSet("record", flag.ContinueOnError)
	taskFlag := addTaskFlag(fs)
	layoutFlag := addLayoutFlag(fs)
	acFlag := fs.Bool("ac", false, "Record AC = true")
	noAcFlag := fs.Bool("no-ac", false, "Record AC = false")
	edFlag := fs.Bool("editorial", false, "Record editorial viewed = true")
	noEdFlag := fs.Bool("no-editorial", false, "Record editorial viewed = false")
	scoreFlag := fs.String("score", "", "5-axis score k,t,c,i,v (each 0-3), e.g. 2,3,2,3,1")
	kFlag := fs.Int("knowledge", -1, "knowledge score 0-3")
	tFlag := fs.Int("translation", -1, "translation score 0-3")
	cFlag := fs.Int("complexity", -1, "complexity score 0-3")
	iFlag := fs.Int("impl", -1, "impl score 0-3")
	vFlag := fs.Int("verify", -1, "verify score 0-3")
	timeFlag := fs.String("time", "", "Override implementation time (e.g. 25m, 1h5m)")
	fs.SetOutput(os.Stderr)
	if err := fs.Parse(flagArgs); err != nil {
		return 2, err
	}
	task, code, err := requireTask(*taskFlag, contest)
	if err != nil {
		return code, err
	}

	ac, err := resolveTriBool(*acFlag, *noAcFlag, "--ac", "--no-ac")
	if err != nil {
		return 2, err
	}
	editorial, err := resolveTriBool(*edFlag, *noEdFlag, "--editorial", "--no-editorial")
	if err != nil {
		return 2, err
	}
	score, err := resolveScoreFlags(*scoreFlag, *kFlag, *tFlag, *cFlag, *iFlag, *vFlag)
	if err != nil {
		return 2, err
	}
	var overrideMs int64
	if *timeFlag != "" {
		overrideMs, err = parseDurationMs(*timeFlag)
		if err != nil {
			return 2, err
		}
	}

	rt, err := buildRecordTarget(*layoutFlag, contest, task)
	if err != nil {
		return 2, err
	}
	st, _, err := solvestat.ReadFile(rt.path)
	if err != nil {
		if os.IsNotExist(err) {
			return 1, errors.New("解答ファイルがありません。先に atcoder start か atcoder record start してください")
		}
		return 1, err
	}

	now := time.Now()
	patch := solvestat.Empty()

	// solved_at は未記録のときだけ今に確定する (再実行で完了時刻を動かさない)。
	if st.SolvedAt.IsZero() {
		patch.SolvedAt = now
	}
	solvedAt := st.SolvedAt
	if !patch.SolvedAt.IsZero() {
		solvedAt = patch.SolvedAt
	}

	// 対話プロンプト (TTY かつフラグで与えられていない項目のみ)。
	interactive := term.IsTerminal(int(os.Stdin.Fd()))
	var r *bufio.Reader
	if interactive {
		r = bufio.NewReader(os.Stdin)
		printScoreGuide()
		if ac == nil {
			ac = promptYesNo(r, "AC できましたか? [y/N]: ")
		}
		if editorial == nil {
			editorial = promptYesNo(r, "解説を見ましたか? [y/N]: ")
		}
	}

	// 実装時間の確定: --time 優先 → (未記録なら) started_at 差 → 対話入力。
	// 既に duration が記録済みなら温存する (record 再実行でスコアだけ足すとき壁時計で潰さない)。
	var durMs int64
	switch {
	case overrideMs != 0:
		durMs = overrideMs
	case st.DurationMs > 0:
		durMs = 0 // 温存 (patch では触らない)
	default:
		durMs = resolveDurationMs(0, st, solvedAt)
		if durMs == 0 && interactive {
			if v := promptDuration(r, "実装時間 (例 25m, 空 Enter で未記録) > "); v != 0 {
				durMs = v
			}
		}
	}
	if durMs != 0 {
		durMs = checkAnomalyInteractive(durMs, r)
	}

	// 5 軸: フラグ未指定の軸を対話で埋める。
	if interactive {
		score.Knowledge = promptScoreIfUnset(r, "知識", score.Knowledge)
		score.Translation = promptScoreIfUnset(r, "翻訳", score.Translation)
		score.Complexity = promptScoreIfUnset(r, "計算量", score.Complexity)
		score.Impl = promptScoreIfUnset(r, "実装", score.Impl)
		score.Verify = promptScoreIfUnset(r, "検証", score.Verify)
	}

	if ac != nil {
		patch.AC = ac
	}
	if editorial != nil {
		patch.Editorial = editorial
	}
	patch.Score = score
	if durMs != 0 {
		patch.DurationMs = durMs
	}
	if tms := rt.targetMs(); tms > 0 {
		patch.TargetMs = tms
	}

	if err := solvestat.Update(rt.path, patch); err != nil {
		return 1, err
	}

	// 書き込んだ内容を要約表示。
	final, _, _ := solvestat.ReadFile(rt.path)
	fmt.Printf("記録しました: %s\n", rt.path)
	printTimeLine(final.DurationMs, final.TargetMs)
	printRecordSummary(final)
	return 0, nil
}

// resolveTriBool は 相反 bool フラグペアを tri-state (*bool) に畳む。両立指定は error。
func resolveTriBool(yes, no bool, yesName, noName string) (*bool, error) {
	if yes && no {
		return nil, fmt.Errorf("%s と %s は同時に指定できません", yesName, noName)
	}
	if yes {
		return solvestat.BoolPtr(true), nil
	}
	if no {
		return solvestat.BoolPtr(false), nil
	}
	return nil, nil
}

// resolveScoreFlags は --score (CSV) と個別軸フラグを合成する。個別軸が --score より優先。
func resolveScoreFlags(csv string, k, t, c, i, v int) (solvestat.Score, error) {
	score := solvestat.Score{Knowledge: -1, Translation: -1, Complexity: -1, Impl: -1, Verify: -1}
	if csv != "" {
		parts := strings.Split(csv, ",")
		if len(parts) != 5 {
			return score, fmt.Errorf("--score は 5 値 (k,t,c,i,v) で指定してください: %q", csv)
		}
		dst := []*int{&score.Knowledge, &score.Translation, &score.Complexity, &score.Impl, &score.Verify}
		for idx, p := range parts {
			n, err := strconv.Atoi(strings.TrimSpace(p))
			if err != nil || n < 0 || n > 3 {
				return score, fmt.Errorf("--score の各値は 0-3 の整数: %q", p)
			}
			*dst[idx] = n
		}
	}
	// 個別軸で上書き (0-3 の範囲チェック)。
	for _, f := range []struct {
		name string
		val  int
		dst  *int
	}{
		{"--knowledge", k, &score.Knowledge},
		{"--translation", t, &score.Translation},
		{"--complexity", c, &score.Complexity},
		{"--impl", i, &score.Impl},
		{"--verify", v, &score.Verify},
	} {
		if f.val == -1 {
			continue // 未指定
		}
		if f.val < 0 || f.val > 3 {
			return score, fmt.Errorf("%s は 0-3 で指定してください: %d", f.name, f.val)
		}
		*f.dst = f.val
	}
	return score, nil
}

// parseDurationMs は duration 文字列をミリ秒に変換する。
func parseDurationMs(s string) (int64, error) {
	d, err := time.ParseDuration(strings.TrimSpace(s))
	if err != nil {
		return 0, fmt.Errorf("--time が duration として不正です (例 25m, 1h5m): %q", s)
	}
	return d.Milliseconds(), nil
}

// resolveDurationMs は実装時間 (ms) を決める。override 優先、無ければ started_at 差。
// どちらも無ければ 0 (未計測)。
func resolveDurationMs(overrideMs int64, st solvestat.Stat, solvedAt time.Time) int64 {
	if overrideMs != 0 {
		return overrideMs
	}
	if !st.StartedAt.IsZero() && !solvedAt.IsZero() {
		return solvedAt.Sub(st.StartedAt).Milliseconds()
	}
	return 0
}

// checkAnomaly は異常値 (負値 / 12h 超) を warning しつつ値をそのまま返す (非対話向け)。
func checkAnomaly(durMs int64) int64 {
	if durMs < 0 || durMs > maxDurationMs {
		fmt.Fprintf(os.Stderr, "warning: 実装時間 %s が異常値です (負値 / 12h 超)。そのまま記録します。\n", fmtDurMs(durMs))
	}
	return durMs
}

// checkAnomalyInteractive は異常値のとき対話で選ばせる。非 r (非対話) は checkAnomaly。
func checkAnomalyInteractive(durMs int64, r *bufio.Reader) int64 {
	if durMs >= 0 && durMs <= maxDurationMs {
		return durMs
	}
	if r == nil {
		return checkAnomaly(durMs)
	}
	fmt.Fprintf(os.Stderr, "実装時間 %s は異常値です。この値で記録しますか? [y/N] (N で手入力) : ", fmtDurMs(durMs))
	line, _ := r.ReadString('\n')
	if ans := strings.ToLower(strings.TrimSpace(line)); ans == "y" || ans == "yes" {
		return durMs
	}
	if v := promptDuration(r, "実装時間 (例 25m, 空 Enter で未記録) > "); v != 0 {
		return v
	}
	return 0
}

func printScoreGuide() {
	fmt.Fprintln(os.Stderr, "5 軸スコア目安: 0=手が出ず / 1=大きくつまずいた / 2=手間取った / 3=スムーズ")
}

func promptYesNo(r *bufio.Reader, prompt string) *bool {
	fmt.Fprint(os.Stderr, prompt)
	line, _ := r.ReadString('\n')
	ans := strings.ToLower(strings.TrimSpace(line))
	if ans == "" {
		return solvestat.BoolPtr(false) // 既定 N
	}
	return solvestat.BoolPtr(ans == "y" || ans == "yes")
}

func promptDuration(r *bufio.Reader, prompt string) int64 {
	fmt.Fprint(os.Stderr, prompt)
	line, _ := r.ReadString('\n')
	s := strings.TrimSpace(line)
	if s == "" {
		return 0
	}
	ms, err := parseDurationMs(s)
	if err != nil {
		fmt.Fprintln(os.Stderr, "  (不正な duration。未記録にします)")
		return 0
	}
	return ms
}

func promptScoreIfUnset(r *bufio.Reader, label string, cur int) int {
	if cur >= 0 {
		return cur // フラグ指定済み
	}
	for {
		fmt.Fprintf(os.Stderr, "%s [0-3, 空 Enter で未記録] > ", label)
		line, _ := r.ReadString('\n')
		s := strings.TrimSpace(line)
		if s == "" {
			return -1
		}
		n, err := strconv.Atoi(s)
		if err == nil && n >= 0 && n <= 3 {
			return n
		}
		fmt.Fprintln(os.Stderr, "  (0-3 の整数で入力してください)")
	}
}

// printTimeLine は実装時間 (と目標比) の 1 行を出す。durMs=0 は未計測。
func printTimeLine(durMs, targetMs int64) {
	if durMs == 0 {
		fmt.Println("  実装時間: 未計測")
		return
	}
	if targetMs <= 0 {
		fmt.Printf("  実装 %s (目標未設定)\n", fmtDurMs(durMs))
		return
	}
	diff := durMs - targetMs
	label := "達成"
	sign := "-"
	mag := -diff
	if diff > 0 {
		label = "超過"
		sign = "+"
		mag = diff
	}
	fmt.Printf("  実装 %s / 目標 %s (%s%s, %s)\n", fmtDurMs(durMs), fmtDurMs(targetMs), sign, fmtDurMs(mag), label)
}

// printRecordSummary は ac/editorial/score の要約行を出す。
func printRecordSummary(st solvestat.Stat) {
	fmt.Printf("  ac=%s  editorial=%s\n", boolStr(st.AC), boolStr(st.Editorial))
	fmt.Printf("  score  k=%s t=%s c=%s i=%s v=%s\n",
		scoreStr(st.Score.Knowledge), scoreStr(st.Score.Translation), scoreStr(st.Score.Complexity),
		scoreStr(st.Score.Impl), scoreStr(st.Score.Verify))
}

func boolStr(b *bool) string {
	if b == nil {
		return "-"
	}
	return strconv.FormatBool(*b)
}

func scoreStr(n int) string {
	if n < 0 {
		return "-"
	}
	return strconv.Itoa(n)
}

// fmtDurMs は ms を分単位に丸めた compact 表記 ("23m" / "1h5m") にする。
func fmtDurMs(ms int64) string {
	neg := ms < 0
	if neg {
		ms = -ms
	}
	m := int(time.Duration(ms) * time.Millisecond / time.Minute)
	var s string
	if m < 60 {
		s = fmt.Sprintf("%dm", m)
	} else {
		s = fmt.Sprintf("%dh%dm", m/60, m%60)
	}
	if neg {
		return "-" + s
	}
	return s
}
