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

	q := inInt()
	var heads, lengths []int
	var cursor int
	for range q {
		query := inInt()
		switch query {
		case 1:
			// 末尾に追加
			l := inInt()
			var h int
			if len(heads) != 0 {
				h = heads[len(heads)-1] + lengths[len(heads)-1]
			}
			lengths = append(lengths, l)
			heads = append(heads, h)
		case 2:
			// 先頭から pop
			cursor++
		case 3:
			// k 番目の蛇の頭の座標
			k := inInt() - 1
			head := heads[cursor+k]
			if cursor > 0 {
				head -= heads[cursor-1] + lengths[cursor-1]
			}
			out(head)
		}
	}
}
