package main

import (
	"bufio"
	"fmt"
	"math"
	"os"
	"slices"
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
	k := inInt()

	a := make([]int, n)
	for i := range n {
		a[i] = inInt()
	}

	aa := make([][]int, k)
	for i := range n {
		aa[i%k] = append(aa[i%k], a[i])
	}
	for i := range k {
		slices.Sort(aa[i])
	}

	b := make([]int, n)

	for i := range n {
		b[i] = aa[i%k][i/k]
	}

	yesno(slices.IsSorted(b))
}
