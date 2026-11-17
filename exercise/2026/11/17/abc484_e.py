# >>> atcoder-stat >>>
# started_at  = 2026-11-17T08:09:13+09:00
# solved_at   = 2026-11-17T08:43:29+09:00
# duration_ms = 2056360
# ac          = true
# editorial   = true
# knowledge   = 2
# translation = 1
# complexity  = 2
# impl        = 2
# verify      = 2
# <<< atcoder-stat <<<
from bisect import bisect_left, bisect_right
from itertools import accumulate
from typing import cast

from atcoder.fenwicktree import FenwickTree

N, L, R = map(int, input().split())
(*A,) = map(int, input().split())

(*prefix,) = accumulate(A, initial=0)
compressed = sorted(set(prefix))

bit = FenwickTree(len(compressed))
ans = 0
for p in prefix:
    l = bisect_left(compressed, p - R)
    r = bisect_right(compressed, p - L)
    ans += cast(int, bit.sum(l, r))
    bit.add(bisect_left(compressed, p), 1)
print(ans)
