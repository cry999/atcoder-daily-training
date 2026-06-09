package main

import (
	"errors"
	"fmt"

	"github.com/cry999/atcoder-daily-training/internal/config"
)

// cmdConfig は `atcoder config <show|get|set|path>` を処理し、ユーザ設定
// (config.toml) の閲覧・編集を行う。
//
// exit code: 引数誤り / 未知キー / 型不一致 / 既存 config の文法エラー = 2、
// config.toml の書き込み失敗 = 1、成功 = 0。
func cmdConfig(args []string) (int, error) {
	if len(args) == 0 {
		return 2, errors.New("usage: atcoder config <show|get|set|path>")
	}
	switch args[0] {
	case "show":
		return configShow()
	case "get":
		return configGet(args[1:])
	case "set":
		return configSet(args[1:])
	case "path":
		fmt.Println(config.Path())
		return 0, nil
	default:
		return 2, fmt.Errorf("unknown config subcommand: %s (want show, get, set, or path)", args[0])
	}
}

func configShow() (int, error) {
	kvs, err := config.All()
	if err != nil {
		return 2, err // 既存 config の文法エラー (ErrParse)
	}
	for _, kv := range kvs {
		fmt.Printf("%s = %s\n", kv.Key, kv.Value)
	}
	return 0, nil
}

func configGet(args []string) (int, error) {
	if len(args) < 1 {
		return 2, errors.New("usage: atcoder config get <key>")
	}
	v, err := config.Get(args[0])
	if err != nil {
		// 未知キー (ErrUnknownKey) も既存 config の文法エラー (ErrParse) も設定エラー。
		return 2, err
	}
	fmt.Println(v)
	return 0, nil
}

func configSet(args []string) (int, error) {
	if len(args) < 2 {
		return 2, errors.New("usage: atcoder config set <key> <value>")
	}
	key, value := args[0], args[1]
	if err := config.Set(key, value); err != nil {
		// 未知キー / 型不一致 / 文法エラーは設定エラー (exit 2)、それ以外
		// (書き込み失敗等) は実行時エラー (exit 1)。
		if errors.Is(err, config.ErrUnknownKey) ||
			errors.Is(err, config.ErrInvalidValue) ||
			errors.Is(err, config.ErrParse) {
			return 2, err
		}
		return 1, err
	}
	fmt.Printf("set %s = %s  (%s)\n", key, value, config.Path())
	return 0, nil
}
