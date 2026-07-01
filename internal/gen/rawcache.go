package gen

import (
	"os"
	"time"

	"github.com/BurntSushi/toml"
)

// Raw は gen.toml に保存する解析元の生セクション (ADR 0008: 解析済み構造ではなく
// 生テキストを source-of-truth にする)。fetch で問題ページから抽出し、gen が読む。
type Raw struct {
	FetchedAt   time.Time
	InputFormat string // 入力形式節の InnerText
	Constraints string // 制約節の InnerText
}

// genFile は gen.toml のオンディスク表現。
type genFile struct {
	FetchedAt time.Time `toml:"fetched_at"`
	Raw       rawTable  `toml:"raw"`
}

type rawTable struct {
	InputFormat string `toml:"input_format"`
	Constraints string `toml:"constraints"`
}

// Load は gen.toml を読む。ファイルが無い / 壊れている場合は error。
func Load(path string) (*Raw, error) {
	var gf genFile
	if _, err := toml.DecodeFile(path, &gf); err != nil {
		return nil, err
	}
	return &Raw{
		FetchedAt:   gf.FetchedAt,
		InputFormat: gf.Raw.InputFormat,
		Constraints: gf.Raw.Constraints,
	}, nil
}

// Save は gen.toml を書き出す。ディレクトリは呼び出し側が用意しておくこと。
func Save(path string, r *Raw) error {
	f, err := os.Create(path)
	if err != nil {
		return err
	}
	defer f.Close()
	gf := genFile{
		FetchedAt: r.FetchedAt,
		Raw:       rawTable{InputFormat: r.InputFormat, Constraints: r.Constraints},
	}
	return toml.NewEncoder(f).Encode(gf)
}

// HasContent は解析に使える生テキストが 1 つでもあるかを返す。
func (r *Raw) HasContent() bool {
	return r != nil && (r.InputFormat != "" || r.Constraints != "")
}
