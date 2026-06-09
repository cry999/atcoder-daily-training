package main

import (
	"errors"
	"fmt"
	"os"

	"github.com/cry999/atcoder-daily-training/internal/complete"
)

// cmdCompletion は `atcoder completion <shell>` を処理し、指定シェル用の補完
// スクリプトを stdout に出力する。副作用は無い (ファイルもネットワークも触らない)。
func cmdCompletion(args []string) (int, error) {
	if len(args) < 1 {
		return 2, errors.New("shell is required (bash, zsh, or fish)")
	}
	var script string
	switch args[0] {
	case "bash":
		script = bashCompletion
	case "zsh":
		script = zshCompletion
	case "fish":
		script = fishCompletion
	default:
		return 2, fmt.Errorf("unsupported shell: %s (want bash, zsh, or fish)", args[0])
	}
	fmt.Print(script)
	return 0, nil
}

// cmdComplete は隠しヘルパ `atcoder __complete -- <words...>` を処理する。補完
// スクリプトからのみ呼ばれ、次単語の候補を 1 行 1 件で出力する。補完を壊さない
// ため常に exit 0 で終える (error は返さない)。
func cmdComplete(args []string) (int, error) {
	words := args
	if len(words) > 0 && words[0] == "--" {
		words = words[1:]
	}
	root, err := os.Getwd()
	if err != nil {
		root = "."
	}
	for _, c := range complete.Complete(root, words) {
		fmt.Println(c)
	}
	return 0, nil
}

// 各シェルの補完スクリプト。候補生成は丸ごと `atcoder __complete` に委譲し、ここでは
// 現在のトークン列を渡して結果を並べるだけに保つ (シェル間でロジックを重複させない)。

const bashCompletion = `# bash completion for atcoder. Load with: source <(atcoder completion bash)
_atcoder() {
  local cur cands
  cur="${COMP_WORDS[COMP_CWORD]}"
  cands="$(atcoder __complete -- "${COMP_WORDS[@]:1:COMP_CWORD}")"
  COMPREPLY=( $(compgen -W "${cands}" -- "${cur}") )
}
complete -F _atcoder atcoder
`

const zshCompletion = `#compdef atcoder
# zsh completion for atcoder. Load with: source <(atcoder completion zsh)
_atcoder() {
  local -a cands
  cands=(${(f)"$(atcoder __complete -- ${words[2,$CURRENT]})"})
  compadd -- $cands
}
compdef _atcoder atcoder
`

const fishCompletion = `# fish completion for atcoder. Load with: atcoder completion fish | source
function __atcoder_complete
    set -l tokens (commandline -opc) (commandline -ct)
    atcoder __complete -- $tokens[2..-1]
end
complete -c atcoder -f -a '(__atcoder_complete)'
`
