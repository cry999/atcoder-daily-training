# >>> atcoder-stat >>>
# started_at  = 2026-10-09T12:36:09+09:00
# solved_at   = 2026-10-09T12:54:39+09:00
# duration_ms = 1110875
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from atcoder.segtree import SegTree
import sys

input = sys.stdin.readline

N, Q = map(int, input().split())
(*A,) = map(int, input().split())

# (最大の値, 2 番目に大きい値, 1 番目の個数, 2 番目の個数)


def op(x: tuple[int, ...], y: tuple[int, ...]):
    a, b, ca, cb = x
    c, d, cc, cd = y

    if a == c:
        # 最大値が同じ
        if b > d:
            return (a, b, ca + cc, cb)
        if b < d:
            return (a, d, ca + cc, cd)
        return (a, b, ca + cc, cb + cd)

    # a > c となるように入れ替える
    if a < c:
        a, b, ca, cb, c, d, cc, cd = c, d, cc, cd, a, b, ca, cb

    # 最大値は a。2番目の候補は b と c
    if b > c:
        return (a, b, ca, cb)
    if b < c:
        return (a, c, ca, cc)
    return (a, b, ca, cb + cc)


e = (-1, -1, 0, 0)

seg = SegTree(op, e, [(a, -1, 1, 0) for a in A])

ans = []
for _ in range(Q):
    q, *args = map(int, input().split())
    if q == 1:
        p, x = args
        seg.set(p - 1, (x, -1, 1, 0))
    else:
        l, r = args
        ans.append(str(seg.prod(l - 1, r)[3]))
print("\n".join(ans))
