package main

import (
	"bufio"
	"fmt"
	"math"
	"os"
	"strconv"
)

var sc = bufio.NewScanner(os.Stdin)
var wr = bufio.NewWriter(os.Stdout)

func must[T any](v T, err error) T {
	if err != nil {
		panic(err)
	}
	return v
}

func out(x ...any) {
	fmt.Fprintln(wr, x...)
}

func inInt() int {
	return must(strconv.Atoi(in()))
}

func in() string {
	sc.Scan()
	return sc.Text()
}

func yesno(b bool) {
	if b {
		out("Yes")
	} else {
		out("No")
	}
}

func main() {
	defer wr.Flush()
	sc.Split(bufio.ScanWords)
	sc.Buffer([]byte{}, math.MaxInt32)

	s := in()
	q := inInt()
	k := make([]int, q)
	for i := range q {
		k[i] = inInt()
	}

	ans := make([]any, 0, q)
	for _, ki := range k {
		d := (ki - 1) / len(s)
		// d のビットの個数が偶数なら s (大文字小文字がオリジナル) で
		// 奇数なら t (大文字小文字が反転) になる。
		// 文字自体は (ki-1) % len(s)
		i := (ki - 1) % len(s)

		var bits int
		for d > 0 {
			if d&1 == 1 {
				bits += 1
			}
			d >>= 1
		}

		c := s[i]
		if bits%2 == 0 {
			ans = append(ans, string(c))
		} else {
			if 'a' <= c && c <= 'z' {
				ans = append(ans, string(c-'a'+'A'))
			} else {
				ans = append(ans, string(c-'A'+'a'))
			}
		}
	}
	out(ans...)
}
