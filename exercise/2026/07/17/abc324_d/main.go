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

func eqMap[K, V comparable](m1, m2 map[K]V) bool {
	if len(m1) != len(m2) {
		return false
	}
	for k, v := range m1 {
		if m2[k] != v {
			return false
		}
	}
	return true
}

func main() {
	defer wr.Flush()
	sc.Split(bufio.ScanWords)
	sc.Buffer([]byte{}, math.MaxInt32)

	n := inInt()
	s := in()
	counter := map[int]int{}
	for _, c := range s {
		counter[int(c-'0')]++
	}

	var ans int
	for i := range 10_000_000 {
		d := i * i
		counter2 := map[int]int{}
		for range n {
			counter2[d%10]++
			d /= 10
		}
		if d > 0 {
			break
		}

		if eqMap(counter, counter2) {
			ans++
		}
	}
	out(ans)
}
