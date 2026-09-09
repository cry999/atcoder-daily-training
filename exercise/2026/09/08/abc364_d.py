# >>> atcoder-stat >>>
# started_at  = 2026-09-08T09:19:55+09:00
# solved_at   = 2026-09-08T09:59:52+09:00
# duration_ms = 2397907
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import sys
from sortedcontainers import SortedList

input = sys.stdin.readline


N, Q = map(int, input().split())
A = SortedList(list(map(int, input().split())))

for _ in range(Q):
    b, k = map(int, input().split())

    # abs(b - A[j]) を満たす j が k 個になる d を二分探索?
    lo, hi = -1, 10**9
    while hi - lo > 1:
        mid = (lo + hi) // 2
        i = A.bisect_left(b - mid)
        j = A.bisect_right(b + mid)
        if j - i >= k:
            hi = mid
        else:
            lo = mid

    print(hi)
