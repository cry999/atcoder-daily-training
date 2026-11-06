package main

import (
	"bufio"
	"fmt"
	"os"
)

func main() {
	in := bufio.NewReader(os.Stdin)
	out := bufio.NewWriter(os.Stdout)
	defer out.Flush()

	var n int64
	var m int
	fmt.Fscan(in, &n, &m)

	seen := make([]bool, m)
	divisors := make([]int, 0)

	add := func(d int64) {
		r := int(d % int64(m))
		if !seen[r] {
			seen[r] = true
			divisors = append(divisors, r)
		}
	}

	for d := int64(1); d*d <= n; d++ {
		if n%d == 0 {
			add(d)
			add(n / d)
		}
	}

	ans := make([]int, m)
	for i := range ans {
		ans[i] = -1
	}

	queue := make([]int, 0, m)
	for _, d := range divisors {
		ans[d] = 1
		queue = append(queue, d)
	}

	for head := 0; head < len(queue) && len(queue) < m; head++ {
		r := queue[head]
		next := ans[r] + 1

		for _, d := range divisors {
			x := int(int64(r) * int64(d) % int64(m))
			if ans[x] != -1 {
				continue
			}
			ans[x] = next
			queue = append(queue, x)

			if len(queue) == m {
				break
			}
		}
	}

	for _, v := range ans {
		fmt.Fprintln(out, v)
	}
}
