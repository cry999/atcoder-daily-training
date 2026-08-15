# >>> atcoder-stat >>>
# started_at  = 2026-08-08T09:09:17+09:00
# solved_at   = 2026-08-08T09:16:02+09:00
# duration_ms = 405755
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from atcoder.segtree import SegTree

N, D = map(int, input().split())
(*A,) = map(int, input().split())
MAX_A = max(A)

seg = SegTree(op=max, e=0, v=[0] * (MAX_A + 1))
for a in A:
    max_len = seg.prod(max(0, a - D), min(MAX_A, a + D) + 1)
    seg.set(a, max_len + 1)

print(seg.all_prod())
