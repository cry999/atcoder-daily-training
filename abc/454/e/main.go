package main

import (
	"bufio"
	"bytes"
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
	sc.Scan()

	return must(strconv.Atoi(sc.Text()))
}

func main() {
	defer wr.Flush()
	sc.Split(bufio.ScanWords)
	sc.Buffer([]byte{}, math.MaxInt32)

	t := inInt()
	for range t {
		n := inInt()
		a := inInt()
		b := inInt()

		if n%2 == 1 {
			out("No")
			continue
		}

		if (a+b)%2 == 0 {
			out("No")
			continue
		}

		routes := []byte{}

		ls := bytes.Repeat([]byte{'L'}, n-1)
		rs := bytes.Repeat([]byte{'R'}, n-1)

		bh1 := make([]byte, 0, 2*n)
		bh1 = append(bh1, rs...)
		bh1 = append(bh1, 'D')
		bh1 = append(bh1, ls...)
		bh1 = append(bh1, 'D')

		bh2 := slices.Clone(bh1)
		slices.Reverse(bh2)

		bw1 := []byte{'D', 'R', 'U', 'R'}

		bw2 := slices.Clone(bw1)
		slices.Reverse(bw2)

		nh := 0
		for a-nh > 2 {
			routes = append(routes, bh1...)
			nh += 2
		}

		nw := 0
		for b-nw > 2 {
			routes = append(routes, bw1...)
			nw += 2
		}

		if b%2 == 1 {
			routes = append(routes, 'R', 'D')
		} else {
			routes = append(routes, 'D', 'R')
		}
		nw += 2

		for n-nw > 0 {
			routes = append(routes, bw2...)
			nw += 2
		}
		nh += 2

		for n-nh > 0 {
			routes = append(routes, bh2...)
			nh += 2
		}

		out("Yes")
		out(string(routes))
	}
}
