package main

import (
	"math/rand"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/gen"
	"github.com/cry999/atcoder-daily-training/internal/testexec"
)

// chatGenFunc は chat の :gen フック (要件 060)。CLI `atcoder gen` と同じく、gen.toml の
// 生セクション (無ければ fetch) を解析し、制約 / 入力形式からランダム入力を 1 つ生成する。
// chat (TUI) から非同期に呼ばれるため、取得進捗は stdout を汚さないサイレント reporter
// で握りつぶし、生成入力と取りこぼし警告を返す (chat が入力欄へ前埋め + 警告を info 行で表示)。
func chatGenFunc(contest, task string) func() (string, []string, error) {
	return func() (string, []string, error) {
		reporter := testexec.NewSummaryReporter()
		raw, err := testexec.EnsureGenSource(reporter, contest, task, false)
		if err != nil {
			return "", nil, err
		}
		spec, err := gen.ParseSpec(*raw)
		if err != nil {
			return "", nil, err
		}
		rng := rand.New(rand.NewSource(time.Now().UnixNano()))
		input, err := spec.Generate(rng, gen.SizeRandom)
		if err != nil {
			return "", nil, err
		}
		return string(input), spec.Warnings, nil
	}
}
