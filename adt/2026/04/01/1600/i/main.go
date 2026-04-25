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

func in() []byte {
	sc.Scan()
	return []byte(sc.Text())
}

type Segtree struct {
	n    int
	data []int
}

func NewSegtree(n int) *Segtree {
	st := new(Segtree)
	st.n = 1

	for st.n < n {
		st.n *= 2
	}
	st.data = make([]int, 2*st.n)

	return st
}

func (st *Segtree) Add(i, x int) {
	i += st.n
	st.data[i] += x

	for i >= 2 {
		i /= 2
		st.data[i] = st.data[i*2] + st.data[i*2+1]
	}
}

func (st *Segtree) Query(l, r int) int {
	return st.query(l, r, 1, 0, st.n)
}

func (st *Segtree) query(l, r, k, a, b int) int {
	if r <= a || b <= l {
		return 0
	}
	if l <= a && b <= r {
		return st.data[k]
	}

	return st.query(l, r, k*2, a, (a+b)/2) + st.query(l, r, k*2+1, (a+b)/2, b)
}

func main() {
	defer wr.Flush()
	sc.Split(bufio.ScanWords)
	sc.Buffer([]byte{}, math.MaxInt32)

	n := inInt()
	s := in()
	q := inInt()

	const alpha = 26

	segtrees := make([]*Segtree, alpha)
	total := make([]int, alpha)
	for i := range alpha {
		segtrees[i] = NewSegtree(n + 1)
	}

	for i, c := range s {
		x := int(c - 'a')
		segtrees[x].Add(i, 1)
		total[x]++
	}

	for range q {
		query := inInt()
		switch query {
		case 1:
			x := inInt() - 1
			segtrees[s[x]-'a'].Add(x, -1)
			total[s[x]-'a']--

			s[x] = in()[0]
			segtrees[s[x]-'a'].Add(x, +1)
			total[s[x]-'a']++
		case 2:
			l := inInt() - 1
			r := inInt() - 1

			cnt := make([]int, alpha)
			minC, maxC := 26, -1
			for c := range 26 {
				cnt[c] = segtrees[c].Query(l, r+1)
				if cnt[c] > 0 {
					minC = min(minC, c)
					maxC = max(maxC, c)
				}
			}

			var offset int
			ok := true
			for c := minC; c <= maxC; c++ {
				if minC < c && c < maxC && cnt[c] != total[c] {
					ok = false
					break
				}

				la := l + offset
				ra := la + cnt[c] - 1
				if ra > r || cnt[c] != segtrees[c].Query(la, ra+1) {
					ok = false
					break
				}
				offset += cnt[c]
			}
			if ok {
				out("Yes")
			} else {
				out("No")
			}
		}
	}
}
