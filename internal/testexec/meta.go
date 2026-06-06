package testexec

import (
	"os"
	"time"

	"github.com/BurntSushi/toml"
)

type meta struct {
	Contest     string    `toml:"contest"`
	Task        string    `toml:"task"`
	URL         string    `toml:"url"`
	TimeLimitMs int       `toml:"time_limit_ms"`
	FetchedAt   time.Time `toml:"fetched_at"`
}

func loadMeta(path string) (*meta, error) {
	var m meta
	if _, err := toml.DecodeFile(path, &m); err != nil {
		return nil, err
	}
	return &m, nil
}

func saveMeta(path string, m *meta) error {
	f, err := os.Create(path)
	if err != nil {
		return err
	}
	defer f.Close()
	return toml.NewEncoder(f).Encode(m)
}
