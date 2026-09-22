# >>> atcoder-stat >>>
# started_at  = 2026-09-21T16:41:49+09:00
# solved_at   = 2026-09-21T16:47:18+09:00
# duration_ms = 329735
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


N, M = map(int, input().split())
(*P,) = map(int, input().split())

INF = float("inf")

min_seg = SegTree(min, INF, P)
max_seg = SegTree(max, -INF, P)
rev = [0] * (N + 1)
for i, p in enumerate(P):
    rev[p] = i

for _ in range(M):
    l, r = map(int, input().split())

    min_p = min_seg.prod(l - 1, r)
    max_p = max_seg.prod(l - 1, r)

    min_i, max_i = rev[min_p], rev[max_p]

    min_seg.set(min_i, max_p), min_seg.set(max_i, min_p)
    max_seg.set(min_i, max_p), max_seg.set(max_i, min_p)
    rev[min_p], rev[max_p] = max_i, min_i

ans = [0] * N
for p in range(1, N + 1):
    ans[rev[p]] = p

print(*ans)
