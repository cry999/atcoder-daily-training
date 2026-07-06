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

	n := inInt()
	x := make([]int, n)
	y := make([]int, n)
	pillars := map[int]map[int]struct{}{}
	isIn := func(x, y int) bool {
		if _, ok := pillars[x]; !ok {
			return false
		}
		if _, ok := pillars[x][y]; !ok {
			return false
		}
		return true
	}

	for i := range n {
		x[i] = inInt()
		y[i] = inInt()
		if pillars[x[i]] == nil {
			pillars[x[i]] = map[int]struct{}{}
		}
		pillars[x[i]][y[i]] = struct{}{}
	}

	var ans int
	for i := range n {
		x0, y0 := x[i], y[i]
		for j := i + 1; j < n; j++ {
			x1, y1 := x[j], y[j]

			x2, y2 := -y1+y0+x0, x1-x0+y0
			if !isIn(x2, y2) {
				continue
			}

			x3, y3 := x1-y1+y0, x1+y1-x0
			if !isIn(x3, y3) {
				continue
			}
			ans = max(ans, (x1-x0)*(x1-x0)+(y1-y0)*(y1-y0))
		}
	}
	out(ans)
}
