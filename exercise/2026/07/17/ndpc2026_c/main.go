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

func main() {
	defer wr.Flush()
	sc.Split(bufio.ScanWords)
	sc.Buffer([]byte{}, math.MaxInt32)

	const (
		ns       = 3
		alphabet = 26
		mod      = 998244353
	)

	n := inInt()
	s := make([][]int, ns)
	for i := range ns {
		ss := in()
		s[i] = make([]int, len(ss))
		for j, c := range ss {
			s[i][j] = int(c - 'a')
		}
	}

	dp := map[int]int{0: 1}

	for range n {
		ndp := map[int]int{}
		for nc := range alphabet {
			for k, v := range dp {
				ks := []int{
					(k / 100) % 10, // k1
					(k / 10) % 10,  // k2
					k % 10,         // k3
				}

				var ng bool
				for i, ki := range ks {
					if s[i][ki] == nc {
						ks[i]++
					}
					ng = ng || ks[i] == len(s[i])
				}
				if ng {
					continue
				}

				var nk int
				for i := range ns {
					nk = nk*10 + ks[i]
				}
				ndp[nk] += v
				ndp[nk] %= mod
			}
		}
		dp = ndp
	}

	var ans int
	for _, v := range dp {
		ans += v
		ans %= mod
	}
	out(ans)
}
