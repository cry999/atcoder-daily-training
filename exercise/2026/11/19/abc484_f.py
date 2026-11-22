# >>> atcoder-stat >>>
# started_at  = 2026-11-19T17:27:24+09:00
# solved_at   = 2026-11-19T17:35:48+09:00
# duration_ms = 504787
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from atcoder.segtree import SegTree

N, Q = map(int, input().split())
(*A,) = map(int, input().split())

V2 = (2, 0)
E = (0, 0)


def op(x: tuple[int, int], y: tuple[int, int]) -> tuple[int, int]:
    if x[0] == 0 or y[0] == 2:
        return y
    if y[0] == 0 or x[0] == 2:
        return x
    return x if x[1] == y[1] else V2


seg = SegTree(op, E, [(1, a) if a != -1 else E for a in A])
for _ in range(Q):
    q, *args = map(int, input().split())
    if q == 1:
        i, x = args
        seg.set(i - 1, (1, x) if x != -1 else E)
    else:
        l, r = args
        print("Yes" if seg.prod(l - 1, r)[0] < 2 else "No")
