# >>> atcoder-stat >>>
# started_at  = 2026-07-09T05:44:50+09:00
# solved_at   = 2026-07-09T06:01:01+09:00
# duration_ms = 971645
# ac          = true
# editorial   = true
# knowledge   = 2
# translation = 2
# complexity  = 3
# impl        = 1
# verify      = 2
# <<< atcoder-stat <<<
from bisect import bisect_right
import sys

input = sys.stdin.readline

N = int(input())
A = [int(input()) for _ in range(N)]

dp = []

for i in range(N):
    x = bisect_right(dp, -A[i])
    if x == len(dp):
        dp.append(-A[i])
    else:
        dp[x] = -A[i]
print(len(dp))
