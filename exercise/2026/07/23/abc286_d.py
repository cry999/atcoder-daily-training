# >>> atcoder-stat >>>
# started_at  = 2026-07-23T07:32:01+09:00
# solved_at   = 2026-07-23T07:38:54+09:00
# duration_ms = 413904
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

input = sys.stdin.readline


N, X = map(int, input().split())
dp = [False] * (X + 1)
dp[0] = True

INF = float("inf")
for _ in range(N):
    A, B = map(int, input().split())
    ndp = [False] * (X + 1)
    last = [-INF] * (X + 1)

    for x in range(X + 1):
        if dp[x]:
            last[x] = x
        elif x >= A:
            last[x] = last[x - A]

        ndp[x] = ndp[x] or dp[x] or last[x] >= x - A * B

    dp = ndp
    if dp[X]:
        break
print("Yes" if dp[X] else "No")
