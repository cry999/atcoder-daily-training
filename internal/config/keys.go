package config

import (
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"time"

	"github.com/BurntSushi/toml"
	"github.com/cry999/atcoder-daily-training/internal/layout"
)

// aliasPrefix は config 上の alias キーの接頭辞 (例 "alias.upd-lo")。
const aliasPrefix = "alias."

// targetPrefix は目標実装時間キーの接頭辞 (例 "target.abc.d")。
const targetPrefix = "target."

// targetCategoryRE / targetLetterRE は target.<category>.<letter> の各要素の許容パターン。
var (
	targetCategoryRE = regexp.MustCompile(`^[a-z0-9]+$`)
	targetLetterRE   = regexp.MustCompile(`^[a-z]$`)
)

// targetParts は key が target キーなら (category, letter) を返す。
// isTarget は接頭辞一致、ok は category×letter の形が妥当か。
func targetParts(key string) (category, letter string, isTarget, ok bool) {
	if !strings.HasPrefix(key, targetPrefix) {
		return "", "", false, false
	}
	parts := strings.Split(key[len(targetPrefix):], ".")
	if len(parts) != 2 {
		return "", "", true, false
	}
	category, letter = parts[0], parts[1]
	ok = targetCategoryRE.MatchString(category) && targetLetterRE.MatchString(letter)
	return category, letter, true, ok
}

// aliasNameRE は alias 名 (alias.<name> の <name>) の許容パターン。英数字・- ・_。
var aliasNameRE = regexp.MustCompile(`^[A-Za-z0-9_-]+$`)

// aliasName は key が alias キーなら <name> を返す。ok は名前が妥当か。
// key が alias 接頭辞を持たないときは name="" ok=false。
func aliasName(key string) (name string, isAlias, ok bool) {
	if !strings.HasPrefix(key, aliasPrefix) {
		return "", false, false
	}
	name = key[len(aliasPrefix):]
	return name, true, name != "" && aliasNameRE.MatchString(name)
}

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
		// editor は start の Ctrl+E (nvim 外フォールバック) で使うエディタコマンド (要件 038)。
		// nvim 内 ($NVIM 在り) は親 nvim へ remote 送信するのでこのキーは効かない。
		// 空白区切りで argv 展開する自由文字列 (例 "nvim -p" / "code -w")。未設定は $EDITOR→nvim。
		key:  "editor",
		kind: "string",
		repr: func(c *Config) string {
			if c.Editor == "" {
				return "(unset)"
			}
			return c.Editor
		},
		set: func(m map[string]any, raw string) error {
			setNested(m, []string{"editor"}, strings.TrimSpace(raw))
			return nil
		},
	},
	{
		// editor_nvim_remote は nvim の :terminal 内 ($NVIM 在り) で Ctrl+E したときの
		// remote ターゲット (要件 041)。current=現在のウィンドウで開く (--remote。タブ再利用)、
		// tab=新規タブ (--remote-tab。要件 038 の旧既定)。未設定は current。nvim 外には効かない。
		key:   "editor_nvim_remote",
		kind:  "enum",
		cands: []string{"current", "tab"},
		repr: func(c *Config) string {
			if c.EditorNvimRemote == "" {
				return "current"
			}
			return c.EditorNvimRemote
		},
		set: func(m map[string]any, raw string) error {
			v := strings.TrimSpace(raw)
			if v != "current" && v != "tab" {
				return fmt.Errorf("%w: %q (editor_nvim_remote は current/tab)", ErrInvalidValue, raw)
			}
			setNested(m, []string{"editor_nvim_remote"}, v)
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
// key が "alias.<name>" なら [alias] から引く (未定義は ErrUnknownKey)。
func Get(key string) (string, error) {
	if cat, let, isTarget, ok := targetParts(key); isTarget {
		if !ok {
			return "", fmt.Errorf("%w: %s (target キーは target.<category>.<letter>)", ErrInvalidValue, key)
		}
		targets, err := Targets()
		if err != nil {
			return "", err
		}
		if sub, found := targets[cat]; found {
			if v, found := sub[let]; found {
				return v, nil
			}
		}
		return "", fmt.Errorf("%w: %s", ErrUnknownKey, key)
	}
	if name, isAlias, ok := aliasName(key); isAlias {
		if !ok {
			return "", fmt.Errorf("%w: %s (alias 名は英数字・-・_ のみ)", ErrInvalidValue, key)
		}
		aliases, err := Aliases()
		if err != nil {
			return "", err
		}
		v, found := aliases[name]
		if !found {
			return "", fmt.Errorf("%w: %s", ErrUnknownKey, key)
		}
		return v, nil
	}
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

// Aliases は [alias] テーブル (名前→コマンド列) を返す。未設定なら空 map。
func Aliases() (map[string]string, error) {
	cfg, err := Load()
	if err != nil {
		return nil, err
	}
	if cfg.Alias == nil {
		return map[string]string{}, nil
	}
	return cfg.Alias, nil
}

// Targets は [target.<category>] テーブル (category→letter→duration 文字列) を返す。
// 未設定なら空 map。
func Targets() (map[string]map[string]string, error) {
	cfg, err := Load()
	if err != nil {
		return nil, err
	}
	if cfg.Target == nil {
		return map[string]map[string]string{}, nil
	}
	return cfg.Target, nil
}

// TargetKeys は補完用に "target.<category>.<letter>" をソートして返す。
func TargetKeys() ([]string, error) {
	targets, err := Targets()
	if err != nil {
		return nil, err
	}
	var out []string
	for cat, sub := range targets {
		for let := range sub {
			out = append(out, targetPrefix+cat+"."+let)
		}
	}
	sort.Strings(out)
	return out, nil
}

// AliasKeys は補完用に "alias.<name>" を名前順で返す。
func AliasKeys() ([]string, error) {
	aliases, err := Aliases()
	if err != nil {
		return nil, err
	}
	out := make([]string, 0, len(aliases))
	for n := range aliases {
		out = append(out, aliasPrefix+n)
	}
	sort.Strings(out)
	return out, nil
}

// All は全既知キーと現在値の組をキー順で返す (config show 用)。
// typed キーに続けて [alias] エントリ ("alias.<name>") を名前順で並べる。
func All() ([]KeyValue, error) {
	cfg, err := Load()
	if err != nil {
		return nil, err
	}
	out := make([]KeyValue, 0, len(fields)+len(cfg.Alias))
	for _, k := range Keys() {
		out = append(out, KeyValue{Key: k, Value: lookup(k).repr(cfg)})
	}
	names := make([]string, 0, len(cfg.Alias))
	for n := range cfg.Alias {
		names = append(names, n)
	}
	sort.Strings(names)
	for _, n := range names {
		out = append(out, KeyValue{Key: aliasPrefix + n, Value: cfg.Alias[n]})
	}
	cats := make([]string, 0, len(cfg.Target))
	for c := range cfg.Target {
		cats = append(cats, c)
	}
	sort.Strings(cats)
	for _, c := range cats {
		lets := make([]string, 0, len(cfg.Target[c]))
		for l := range cfg.Target[c] {
			lets = append(lets, l)
		}
		sort.Strings(lets)
		for _, l := range lets {
			out = append(out, KeyValue{Key: targetPrefix + c + "." + l, Value: cfg.Target[c][l]})
		}
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
	if cat, let, isTarget, ok := targetParts(key); isTarget {
		if !ok {
			return fmt.Errorf("%w: %s (target キーは target.<category>.<letter>)", ErrInvalidValue, key)
		}
		v := strings.TrimSpace(raw)
		if _, err := time.ParseDuration(v); err != nil {
			return fmt.Errorf("%w: %q (target は duration 文字列: 35m, 1h5m)", ErrInvalidValue, raw)
		}
		m, err := loadRaw()
		if err != nil {
			return err
		}
		setNested(m, []string{"target", cat, let}, v)
		return saveRaw(m)
	}
	if name, isAlias, ok := aliasName(key); isAlias {
		if !ok {
			return fmt.Errorf("%w: %s (alias 名は英数字・-・_ のみ)", ErrInvalidValue, key)
		}
		m, err := loadRaw()
		if err != nil {
			return err
		}
		setNested(m, []string{"alias", name}, raw)
		return saveRaw(m)
	}
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

// Unset は key を config.toml から削除する。
//   - "alias.<name>": [alias] から該当エントリを削除。未定義は ErrUnknownKey。
//   - typed キー: 上書きを消して既定値に戻す (未設定でも既知キーなら no-op で成功)。
//   - それ以外の未知キー: ErrUnknownKey。
//
// 書き込み失敗はそのまま (= 実行時エラー)。
func Unset(key string) error {
	if cat, let, isTarget, ok := targetParts(key); isTarget {
		if !ok {
			return fmt.Errorf("%w: %s (target キーは target.<category>.<letter>)", ErrInvalidValue, key)
		}
		m, err := loadRaw()
		if err != nil {
			return err
		}
		if !unsetNested(m, []string{"target", cat, let}) {
			return fmt.Errorf("%w: %s", ErrUnknownKey, key)
		}
		return saveRaw(m)
	}
	if name, isAlias, ok := aliasName(key); isAlias {
		if !ok {
			return fmt.Errorf("%w: %s (alias 名は英数字・-・_ のみ)", ErrInvalidValue, key)
		}
		m, err := loadRaw()
		if err != nil {
			return err
		}
		if !unsetNested(m, []string{"alias", name}) {
			return fmt.Errorf("%w: %s", ErrUnknownKey, key)
		}
		return saveRaw(m)
	}
	f := lookup(key)
	if f == nil {
		return fmt.Errorf("%w: %s (known: %s)", ErrUnknownKey, key, strings.Join(Keys(), ", "))
	}
	m, err := loadRaw()
	if err != nil {
		return err
	}
	unsetNested(m, strings.Split(f.key, ".")) // 既知キーは不在でも no-op で成功
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

// unsetNested は m の path で示すエントリを削除する。削除できたら true、
// 中間テーブルやキーが無ければ false。空になった中間テーブルはそのまま残す
// (簡潔さ優先。空テーブルは toml に残るが無害)。
func unsetNested(m map[string]any, path []string) bool {
	cur := m
	for _, k := range path[:len(path)-1] {
		sub, ok := cur[k].(map[string]any)
		if !ok {
			return false
		}
		cur = sub
	}
	last := path[len(path)-1]
	if _, ok := cur[last]; !ok {
		return false
	}
	delete(cur, last)
	return true
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
