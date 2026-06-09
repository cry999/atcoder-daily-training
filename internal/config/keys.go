package config

import (
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"

	"github.com/BurntSushi/toml"
	"github.com/cry999/atcoder-daily-training/internal/layout"
)

// 設定キーの操作で返す sentinel error。呼び出し側 (cmd/atcoder/config.go) が
// exit code を分類するのに使う: ErrUnknownKey / ErrInvalidValue / ErrParse は
// 引数・設定エラー (exit 2)、それ以外 (書き込み失敗等) は実行時エラー (exit 1)。
var (
	ErrUnknownKey   = errors.New("unknown config key")
	ErrInvalidValue = errors.New("invalid config value")
	ErrParse        = errors.New("config parse error")
)

// KeyValue は 1 設定キーと現在値の組 (config show 用)。
type KeyValue struct {
	Key   string
	Value string
}

// field は設定キー 1 つの記述子。既知キー・型・値の get/set を 1 か所に集約する。
// キーを足すときは fields に 1 エントリ追加するだけで config / 補完が対応する。
type field struct {
	key  string // ドットキー (例 "test.side_by_side")
	kind string // 型名。エラーメッセージと値候補に使う ("bool" / "enum" 等)
	// cands は enum キーの取りうる値 (補完候補かつ set のバリデーション元)。
	// 空なら kind=="bool" の既定挙動 (true/false) に委ねる。
	cands []string
	// repr は読み込み済み Config から現在値を文字列で返す (get / show 用)。
	repr func(*Config) string
	// set は raw 文字列をパースし、汎用 map の該当パスへ書き込む (set 用)。
	// パース失敗時は ErrInvalidValue を包んだ error を返す。
	set func(m map[string]any, raw string) error
}

// fields は既知設定キーの登録簿 (単一情報源)。
var fields = []field{
	{
		// layout は test/run/submit 横断の既定レイアウト (トップレベルキー)。
		// 解決順 flag > env > config > auto は layout.Resolve に集約され、ここでは
		// config 層の値だけを読み書きする。未設定 ("") の repr は auto を返す。
		key:   "layout",
		kind:  "enum",
		cands: layout.Names(),
		repr: func(c *Config) string {
			if c.Layout == "" {
				return "auto"
			}
			return c.Layout
		},
		set: func(m map[string]any, raw string) error {
			v := strings.TrimSpace(raw)
			if !layout.Known(v) {
				return fmt.Errorf("%w: %q (layout は %s)", ErrInvalidValue, raw, strings.Join(layout.Names(), "/"))
			}
			setNested(m, []string{"layout"}, v)
			return nil
		},
	},
	{
		key:  "test.side_by_side",
		kind: "bool",
		repr: func(c *Config) string { return strconv.FormatBool(c.Test.SideBySide) },
		set: func(m map[string]any, raw string) error {
			b, err := strconv.ParseBool(strings.TrimSpace(raw))
			if err != nil {
				return fmt.Errorf("%w: %q (test.side_by_side は true/false)", ErrInvalidValue, raw)
			}
			setNested(m, []string{"test", "side_by_side"}, b)
			return nil
		},
	},
}

func lookup(key string) *field {
	for i := range fields {
		if fields[i].key == key {
			return &fields[i]
		}
	}
	return nil
}

// Keys は既知設定キーをソートして返す。
func Keys() []string {
	out := make([]string, len(fields))
	for i := range fields {
		out[i] = fields[i].key
	}
	sort.Strings(out)
	return out
}

// Get は key の現在値 (config.toml 反映後、無ければ既定値) を文字列で返す。
// 未知キーは ErrUnknownKey、既存 config の文法エラーは ErrParse。
func Get(key string) (string, error) {
	f := lookup(key)
	if f == nil {
		return "", fmt.Errorf("%w: %s (known: %s)", ErrUnknownKey, key, strings.Join(Keys(), ", "))
	}
	cfg, err := Load()
	if err != nil {
		return "", err
	}
	return f.repr(cfg), nil
}

// All は全既知キーと現在値の組をキー順で返す (config show 用)。
func All() ([]KeyValue, error) {
	cfg, err := Load()
	if err != nil {
		return nil, err
	}
	out := make([]KeyValue, 0, len(fields))
	for _, k := range Keys() {
		out = append(out, KeyValue{Key: k, Value: lookup(k).repr(cfg)})
	}
	return out, nil
}

// Set は key に raw を書き込む。既存の config.toml を汎用 map で読み、該当キーだけ
// 更新して書き戻す (未知キー・他セクションを保全する)。config.toml が無ければ
// 親 dir ごと作成する。
//
// エラー: 未知キーは ErrUnknownKey、値が型に合わなければ ErrInvalidValue、
// 既存ファイルの文法エラーは ErrParse、書き込み失敗はそのまま (= 実行時エラー)。
func Set(key, raw string) error {
	f := lookup(key)
	if f == nil {
		return fmt.Errorf("%w: %s (known: %s)", ErrUnknownKey, key, strings.Join(Keys(), ", "))
	}
	m, err := loadRaw()
	if err != nil {
		return err
	}
	if err := f.set(m, raw); err != nil {
		return err
	}
	return saveRaw(m)
}

// ValueCandidates は補完用に key の値候補を返す。enum キーは登録された候補、
// bool キーは ["false","true"]、候補が定まらない型は nil。
func ValueCandidates(key string) []string {
	f := lookup(key)
	if f == nil {
		return nil
	}
	if len(f.cands) > 0 {
		out := append([]string(nil), f.cands...)
		sort.Strings(out)
		return out
	}
	if f.kind == "bool" {
		return []string{"false", "true"}
	}
	return nil
}

// loadRaw は config.toml を汎用 map で読む。不在なら空 map。文法エラーは ErrParse。
func loadRaw() (map[string]any, error) {
	m := map[string]any{}
	if _, err := toml.DecodeFile(Path(), &m); err != nil {
		if os.IsNotExist(err) {
			return m, nil
		}
		return nil, fmt.Errorf("%w: %s: %v", ErrParse, Path(), err)
	}
	return m, nil
}

// saveRaw は map を config.toml に書く。親 dir が無ければ作る。
func saveRaw(m map[string]any) error {
	path := Path()
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return err
	}
	f, err := os.Create(path)
	if err != nil {
		return err
	}
	defer f.Close()
	return toml.NewEncoder(f).Encode(m)
}

// setNested は m の path で示すネスト位置に val を置く。中間テーブルが無ければ作る。
func setNested(m map[string]any, path []string, val any) {
	cur := m
	for _, k := range path[:len(path)-1] {
		sub, ok := cur[k].(map[string]any)
		if !ok {
			sub = map[string]any{}
			cur[k] = sub
		}
		cur = sub
	}
	cur[path[len(path)-1]] = val
}
