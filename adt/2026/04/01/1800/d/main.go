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
	sc.Scan()
	return must(strconv.Atoi(sc.Text()))
}

func in() string {
	sc.Scan()
	return sc.Text()
}

func main() {
	defer wr.Flush()
	sc.Split(bufio.ScanWords)
	sc.Buffer([]byte{}, math.MaxInt32)

	n := inInt()
	a := make([]int, n)
	for i := range n {
		a[i] = inInt()
	}

	q := inInt()
	for range q {
		query := inInt()
		switch query {
		case 1:
			k := inInt() - 1
			x := inInt()
			a[k] = x
		case 2:
			k := inInt() - 1
			out(a[k])
		}
	}
}
