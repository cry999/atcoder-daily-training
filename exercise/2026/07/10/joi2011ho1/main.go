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

	h := inInt()
	w := inInt()
	k := inInt()
	fields := make([][][]int, 3)
	for i := range 3 {
		fields[i] = make([][]int, h+1)
		for j := range h + 1 {
			fields[i][j] = make([]int, w+1)
		}
	}

	for i := range h {
		s := in()
		for j := range w {
			var c int
			switch s[j] {
			case 'J':
				c = 0
			case 'O':
				c = 1
			default:
				c = 2
			}
			fields[c][i+1][j+1] = 1
		}
	}

	for i := range h + 1 {
		for j := range w {
			for c := range 3 {
				fields[c][i][j+1] += fields[c][i][j]
			}
		}
	}
	for i := range h {
		for j := range w + 1 {
			for c := range 3 {
				fields[c][i+1][j] += fields[c][i][j]
			}
		}
	}
	ans := make([]any, 3)
	for range k {
		a, b, c, d := inInt(), inInt(), inInt(), inInt()
		for i := range 3 {
			ans[i] = fields[i][c][d] - fields[i][c][b-1] - fields[i][a-1][d] + fields[i][a-1][b-1]
		}
		out(ans...)
	}
}
