package main

import (
	"bufio"
	"fmt"
	"os"
	"sort"
)

type Point struct {
	x, y   int64
	offset int
}

func (p Point) cross(q Point) int64 {
	return p.x*q.y - p.y*q.x
}

func (p Point) half() int {
	if p.y > 0 || (p.y == 0 && p.x > 0) {
		return p.offset
	}
	return 1 + p.offset
}

func solve(in *bufio.Reader) int {
	var n int
	fmt.Fscan(in, &n)

	points := make([]Point, 0, n)
	for i := 0; i < n; i++ {
		var x, y int64
		fmt.Fscan(in, &x, &y)

		if x == 0 && y == 0 {
			continue
		}
		points = append(points, Point{x, y, 0})
	}

	sort.Slice(points, func(i, j int) bool {
		a, b := points[i], points[j]
		ha, hb := a.half(), b.half()
		if ha != hb {
			return ha < hb
		}
		return a.cross(b) > 0
	})

	n = len(points)

	// 一周後の点を追加。半平面番号も 0, 1 → 2, 3 にする。
	for i := 0; i < n; i++ {
		p := points[i]
		points = append(points, Point{p.x, p.y, 2})
	}

	ans, r := 0, 0
	for l := 0; l < n; l++ {
		for r < l+n {
			d := points[r].half() - points[l].half()

			// 角度差が180°未満なら右端を進める。
			if d == 0 || (d == 1 && points[l].cross(points[r]) > 0) {
				r++
			} else {
				break
			}
		}

		if r-l > ans {
			ans = r - l
		}
	}

	return ans
}

func main() {
	in := bufio.NewReader(os.Stdin)
	out := bufio.NewWriter(os.Stdout)
	defer out.Flush()

	var t int
	fmt.Fscan(in, &t)

	for ; t > 0; t-- {
		fmt.Fprintln(out, solve(in))
	}
}
