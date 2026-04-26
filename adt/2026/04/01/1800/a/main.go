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

	r := inInt()
	g := inInt()
	b := inInt()

	c := in()

	var ans int
	switch c {
	case "Red":
		ans = min(g, b)
	case "Green":
		ans = min(r, b)
	case "Blue":
		ans = min(r, g)
	}
	out(ans)
}
