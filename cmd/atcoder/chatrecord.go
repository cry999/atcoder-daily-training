package main

import (
	"errors"
	"fmt"
	"os"
	"strings"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/layout"
	"github.com/cry999/atcoder-daily-training/internal/solvestat"
)

// chatRecordFunc は chat の :record フック (要件 064)。CLI `atcoder record` と同じ
// solve-stat 書き込みロジックを非対話で使い、第 1 トークンで start/stop/(記録本体) を
// dispatch する。chat (TUI) から呼ばれるため stderr には一切出さず、結果・警告・案内は
// すべて行で返す (chat が info/err 行で表示する)。ローカル I/O のみなので同期。
// layout は chat 起動時 (start 分割画面 / test --interactive) に解決済みの lay を受け取り、
// それをそのまま使う (auto 再判定を挟むと abc<NNN> を exercise で解いていても常に ABC
// パスに落ちてしまうため。要件 064)。
func chatRecordFunc(contest, task string, lay layout.Layout) func(args []string) ([]string, error) {
	return func(args []string) ([]string, error) {
		if len(args) >= 1 {
			switch args[0] {
			case "start":
				return chatRecordStart(contest, task, lay, args[1:])
			case "stop":
				return chatRecordStop(contest, task, lay, args[1:])
			}
		}
		return chatRecordMain(contest, task, lay, args)
	}
}

// chatRecordEditLoadFunc は chat の :record edit (要件 066) が編集フォームへ渡す現在値を
// 読み込むフック。解答パスを解決し solve-stat を読んで Stat・目標時間 (config)・記録の有無を
// 返す。ファイルが無い / ブロックが無いときは found=false (フォームは開かず chat が案内する)。
// layout は chat 起動時に解決済みの lay をそのまま使う (chatRecordFunc と同じ理由)。
func chatRecordEditLoadFunc(contest, task string, lay layout.Layout) func() (solvestat.Stat, int64, bool, error) {
	return func() (solvestat.Stat, int64, bool, error) {
		rt, err := recordTargetFor(lay, contest, task)
		if err != nil {
			return solvestat.Empty(), 0, false, err
		}
		st, found, err := solvestat.ReadFile(rt.path)
		if err != nil {
			if os.IsNotExist(err) {
				return solvestat.Empty(), 0, false, nil
			}
			return solvestat.Empty(), 0, false, err
		}
		return st, rt.targetMs(), found, nil
	}
}

// chatRecordEditSaveFunc は :record edit のフォーム確定時に、編集後の Stat を全置換保存する
// フック。started_at / solved_at / target_ms はフォームが元値を温存済み。保存後に読み直して
// 更新結果の要約行を返す (chat が info 行で積む)。
func chatRecordEditSaveFunc(contest, task string, lay layout.Layout) func(solvestat.Stat) ([]string, error) {
	return func(st solvestat.Stat) ([]string, error) {
		rt, err := recordTargetFor(lay, contest, task)
		if err != nil {
			return nil, err
		}
		if err := solvestat.OverwriteFile(rt.path, st); err != nil {
			return nil, err
		}
		final, _, _ := solvestat.ReadFile(rt.path)
		lines := []string{"記録を更新しました: " + rt.path, chatRecordTimeLine(final.DurationMs, final.TargetMs)}
		return append(lines, chatRecordSummaryLines(final)...), nil
	}
}

// chatRecordStart は :record start を処理する (CLI recordStart 相当)。started_at を刻む。
// restart トークンで再計測 (started_at リセット + 完了系クリア)。
func chatRecordStart(contest, task string, lay layout.Layout, args []string) ([]string, error) {
	restart := false
	for _, a := range args {
		if a != "restart" {
			return nil, fmt.Errorf("unknown :record start token %q (want restart)", a)
		}
		restart = true
	}
	rt, err := recordTargetFor(lay, contest, task)
	if err != nil {
		return nil, err
	}
	if err := ensureFileExists(rt.path); err != nil {
		return nil, err
	}
	stamped, warn, err := stampStartedAt(rt.path, restart)
	if err != nil {
		return nil, err
	}
	var lines []string
	if warn != "" {
		lines = append(lines, warn)
	}
	if stamped {
		lines = append(lines, "計測を開始しました: "+rt.path)
	} else {
		lines = append(lines, "計測は継続中です: "+rt.path)
	}
	return lines, nil
}

// chatRecordStop は :record stop を処理する (CLI recordStop 相当)。solved_at を確定し
// duration を算出、target をスナップショットする。ac / time= のみ受ける (スコアは記録本体で)。
func chatRecordStop(contest, task string, lay layout.Layout, args []string) ([]string, error) {
	ac, _, _, overrideMs, err := parseChatRecordTokens(args, false)
	if err != nil {
		return nil, err
	}
	rt, err := recordTargetFor(lay, contest, task)
	if err != nil {
		return nil, err
	}
	st, _, err := solvestat.ReadFile(rt.path)
	if err != nil {
		if os.IsNotExist(err) {
			return nil, errors.New("解答ファイルがありません。先に :record start してください")
		}
		return nil, err
	}

	now := time.Now()
	patch := solvestat.Empty()
	patch.SolvedAt = now
	durMs := resolveDurationMs(overrideMs, st, now)
	var lines []string
	if durMs != 0 {
		if w := chatRecordAnomalyWarn(durMs); w != "" {
			lines = append(lines, w)
		}
		patch.DurationMs = durMs
	}
	if tms := rt.targetMs(); tms > 0 {
		patch.TargetMs = tms
	}
	if ac != nil {
		patch.AC = ac
	}
	if err := solvestat.Update(rt.path, patch); err != nil {
		return nil, err
	}
	lines = append(lines, "計測を終了しました: "+rt.path)
	lines = append(lines, chatRecordTimeLine(durMs, patch.TargetMs))
	lines = append(lines, "スコアは :record ac score=… で記録できます。")
	return lines, nil
}

// chatRecordMain は記録本体 (CLI recordMain の非対話経路相当)。フラグで与えられた
// ac / editorial / score / time を solve-stat へ部分更新で書き戻す。引数なし (:record 単体)
// のときは書き込まず現在値だけ表示する (chat では対話ウィザードを持たないため、記入は
// フラグ経由・閲覧は引数なしに割り当てる)。
func chatRecordMain(contest, task string, lay layout.Layout, args []string) ([]string, error) {
	ac, editorial, score, overrideMs, err := parseChatRecordTokens(args, true)
	if err != nil {
		return nil, err
	}
	rt, err := recordTargetFor(lay, contest, task)
	if err != nil {
		return nil, err
	}
	st, found, err := solvestat.ReadFile(rt.path)
	missing := os.IsNotExist(err)
	if err != nil && !missing {
		return nil, err
	}

	// 引数なし :record → 現在値の表示のみ (書き込まない)。
	if len(args) == 0 {
		if missing || !found {
			return []string{"(まだ記録がありません。:record start で計測を開始できます)"}, nil
		}
		lines := []string{chatRecordTimeLine(st.DurationMs, st.TargetMs)}
		return append(lines, chatRecordSummaryLines(st)...), nil
	}

	if missing {
		return nil, errors.New("解答ファイルがありません。先に :record start してください")
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

	// 実装時間: --time 優先 → 既に duration があれば温存 → started_at 差。
	var durMs int64
	switch {
	case overrideMs != 0:
		durMs = overrideMs
	case st.DurationMs > 0:
		durMs = 0 // 温存 (patch では触らない)
	default:
		durMs = resolveDurationMs(0, st, solvedAt)
	}
	var lines []string
	if durMs != 0 {
		if w := chatRecordAnomalyWarn(durMs); w != "" {
			lines = append(lines, w)
		}
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
		return nil, err
	}

	final, _, _ := solvestat.ReadFile(rt.path)
	lines = append(lines, "記録しました: "+rt.path)
	lines = append(lines, chatRecordTimeLine(final.DurationMs, final.TargetMs))
	return append(lines, chatRecordSummaryLines(final)...), nil
}

// parseChatRecordTokens は :record のトークン列を解釈する。bare 語 ac/noac (と、
// allowScoreEditorial のとき ed/noed)・key=value (score=k,t,c,i,v / time=dur) を受ける。
// 相反する bool の同時指定・score/time の不正値は error (CLI record と同じ検証を流用)。
func parseChatRecordTokens(args []string, allowScoreEditorial bool) (ac, editorial *bool, score solvestat.Score, overrideMs int64, err error) {
	score = solvestat.Score{Knowledge: -1, Translation: -1, Complexity: -1, Impl: -1, Verify: -1}
	var acYes, acNo, edYes, edNo bool
	var scoreCSV, timeStr string
	for _, a := range args {
		switch {
		case a == "ac":
			acYes = true
		case a == "noac" || a == "no-ac":
			acNo = true
		case allowScoreEditorial && (a == "ed" || a == "editorial"):
			edYes = true
		case allowScoreEditorial && (a == "noed" || a == "no-ed" || a == "no-editorial"):
			edNo = true
		case allowScoreEditorial && strings.HasPrefix(a, "score="):
			scoreCSV = strings.TrimPrefix(a, "score=")
		case strings.HasPrefix(a, "time="):
			timeStr = strings.TrimPrefix(a, "time=")
		default:
			return nil, nil, score, 0, fmt.Errorf("unknown :record token %q", a)
		}
	}
	if ac, err = resolveTriBool(acYes, acNo, "ac", "noac"); err != nil {
		return nil, nil, score, 0, err
	}
	if editorial, err = resolveTriBool(edYes, edNo, "ed", "noed"); err != nil {
		return nil, nil, score, 0, err
	}
	if scoreCSV != "" {
		if score, err = resolveScoreFlags(scoreCSV, -1, -1, -1, -1, -1); err != nil {
			return nil, nil, score, 0, err
		}
	}
	if timeStr != "" {
		if overrideMs, err = parseDurationMs(timeStr); err != nil {
			return nil, nil, score, 0, err
		}
	}
	return ac, editorial, score, overrideMs, nil
}

// chatRecordAnomalyWarn は異常値 (負値 / 12h 超) の警告文言を返す (無ければ "")。chat では
// 対話確認を挟めないので、CLI 非対話経路と同じく警告を添えてそのまま記録する。
func chatRecordAnomalyWarn(durMs int64) string {
	if durMs < 0 || durMs > maxDurationMs {
		return "warning: 実装時間 " + fmtDurMs(durMs) + " が異常値です (負値 / 12h 超)。そのまま記録します。"
	}
	return ""
}

// chatRecordTimeLine は実装時間 (と目標比) の 1 行を返す (CLI printTimeLine の行版)。
func chatRecordTimeLine(durMs, targetMs int64) string {
	if durMs == 0 {
		return "  実装時間: 未計測"
	}
	if targetMs <= 0 {
		return fmt.Sprintf("  実装 %s (目標未設定)", fmtDurMs(durMs))
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
	return fmt.Sprintf("  実装 %s / 目標 %s (%s%s, %s)", fmtDurMs(durMs), fmtDurMs(targetMs), sign, fmtDurMs(mag), label)
}

// chatRecordSummaryLines は ac/editorial/score の要約 2 行を返す (CLI printRecordSummary の行版)。
func chatRecordSummaryLines(st solvestat.Stat) []string {
	return []string{
		fmt.Sprintf("  ac=%s  editorial=%s", boolStr(st.AC), boolStr(st.Editorial)),
		fmt.Sprintf("  score  k=%s t=%s c=%s i=%s v=%s",
			scoreStr(st.Score.Knowledge), scoreStr(st.Score.Translation), scoreStr(st.Score.Complexity),
			scoreStr(st.Score.Impl), scoreStr(st.Score.Verify)),
	}
}
