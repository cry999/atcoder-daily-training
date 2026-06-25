package main

import (
	"errors"
	"fmt"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/layout"
	"github.com/cry999/atcoder-daily-training/internal/testexec"
)

// chatMetaShowFunc は chat の :meta 表示フック (要件 055)。CLI `atcoder meta show` と同じく
// キャッシュ済み meta.toml を読み、url / time limit / samples を行に整形して返す。
// field="" なら全体、"url"/"time_limit" なら当該フィールドのみ。未キャッシュは error。
// 行頭ラベルの体裁は `cmd/atcoder/meta.go` の metaShow と揃える。
func chatMetaShowFunc(contest, task string) func(field string) ([]string, error) {
	return func(field string) ([]string, error) {
		m, err := testexec.LoadMeta(contest, task)
		if err != nil {
			return nil, fmt.Errorf("meta が未取得です (atcoder test / meta fetch で取得してください): %s/%s", contest, task)
		}
		urlLine := fmt.Sprintf("url:         %s", metaURLOrNone(m.URL))
		tlLine := fmt.Sprintf("time limit:  %d ms", m.TimeLimitMs)
		switch field {
		case "url":
			return []string{urlLine}, nil
		case "time_limit":
			return []string{tlLine}, nil
		default:
			n, _ := testexec.SampleCount(contest, task)
			return []string{urlLine, tlLine, fmt.Sprintf("samples:     %d", n)}, nil
		}
	}
}

// chatMetaSetFunc は chat の :meta 編集フック (要件 055)。CLI `atcoder meta set --url|--time-limit`
// と同じ検証規則・整形で meta.toml を上書きする:
//   - url: AtCoder の URL (layout.IsTaskURL) のみ。スロット未キャッシュでも空 meta に記録できる。
//   - time_limit: 正の duration (time.ParseDuration) のみ。キャッシュ済みが前提 (未取得なら error)。
//
// 戻り値の newTimeLimitMs は time_limit を更新したときの新値 (chat がヘッダ表示を揃えるのに使う)。
// url 更新時は現在値をそのまま返す。
func chatMetaSetFunc(contest, task string) func(field, value string) ([]string, int, error) {
	return func(field, value string) ([]string, int, error) {
		switch field {
		case "url":
			if !layout.IsTaskURL(value) {
				return nil, 0, fmt.Errorf("--url は AtCoder の URL を指定してください: %q", value)
			}
			// url override はスロット未キャッシュでも記録できる (空の meta を作る)。
			m, err := testexec.LoadMeta(contest, task)
			if err != nil {
				m = &testexec.Meta{Contest: contest, Task: task}
			}
			old := metaURLOrNone(m.URL)
			m.URL = value
			if err := testexec.SaveMeta(contest, task, m); err != nil {
				return nil, 0, err
			}
			return []string{fmt.Sprintf("url:         %s -> %s", old, value)}, m.TimeLimitMs, nil

		case "time_limit":
			dur, err := time.ParseDuration(value)
			if err != nil {
				return nil, 0, fmt.Errorf("--time-limit は duration で指定してください (例: 5s, 1500ms): %q", value)
			}
			if dur <= 0 {
				return nil, 0, errors.New("--time-limit は正の値で指定してください (例: 5s, 1500ms)")
			}
			// time-limit のみの上書きはキャッシュ済みが前提。
			m, err := testexec.LoadMeta(contest, task)
			if err != nil {
				return nil, 0, fmt.Errorf("meta が未取得です (atcoder test / meta fetch で取得してください): %s/%s", contest, task)
			}
			oldMs := m.TimeLimitMs
			m.TimeLimitMs = int(dur / time.Millisecond)
			if err := testexec.SaveMeta(contest, task, m); err != nil {
				return nil, 0, err
			}
			return []string{fmt.Sprintf("time limit:  %d ms -> %d ms", oldMs, m.TimeLimitMs)}, m.TimeLimitMs, nil

		default:
			return nil, 0, fmt.Errorf("unknown meta field %q (want url|time_limit)", field)
		}
	}
}

// chatMetaFetchFunc は chat の :meta fetch 再取得フック (要件 057)。CLI `atcoder meta fetch`
// と同じく meta.toml の url (override 優先・なければ既定 URL) からサンプル + Time Limit を
// 強制再取得し (testexec.EnsureTests refresh=true)、tests/ と meta.toml を更新する。
// chat (TUI) から呼ばれるため、取得進捗は stdout を汚さないサイレント reporter
// (testexec.NewSummaryReporter) で握りつぶし、結果は行で返す (chat が info 行で表示する)。
// 戻り値の newTimeLimitMs は再取得後の Time Limit (chat がヘッダ表示を揃えるのに使う)。
func chatMetaFetchFunc(contest, task string) func() ([]string, int, error) {
	return func() ([]string, int, error) {
		reporter := testexec.NewSummaryReporter()
		res, err := testexec.EnsureTests(reporter, contest, task, true)
		if err != nil {
			return nil, 0, fmt.Errorf("再取得に失敗しました: %w", err)
		}
		m, err := testexec.LoadMeta(contest, task)
		if err != nil {
			return nil, 0, fmt.Errorf("再取得に失敗しました: %w", err)
		}
		lines := []string{
			fmt.Sprintf("fetched %s", task),
			fmt.Sprintf("url:         %s", metaURLOrNone(m.URL)),
			fmt.Sprintf("time limit:  %d ms", res.TimeLimitMs),
			fmt.Sprintf("samples:     %d", res.NumSamples),
		}
		return lines, res.TimeLimitMs, nil
	}
}

// metaURLOrNone は空 url を "(none)" に整形する (CLI meta set と同じ表記)。
func metaURLOrNone(u string) string {
	if u == "" {
		return "(none)"
	}
	return u
}
