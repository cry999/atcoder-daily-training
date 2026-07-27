# >>> atcoder-stat >>>
# started_at  = 2026-07-25T17:35:24+09:00
# solved_at   = 2026-07-25T17:39:40+09:00
# duration_ms = 256000
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 2
# translation = 2
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline


N, X = map(int, input().split())
dp = [False] * (X + 1)
dp[0] = True

INF = 10**18

for _ in range(N):
    a, b = map(int, input().split())

    max_j = [-INF] * (X + 1)
    for j in range(X + 1):
        if dp[j]:
            max_j[j] = j
        elif j - a >= 0:
            max_j[j] = max_j[j - a]

    dp = [max_j[j] >= j - a * b for j in range(X + 1)]

print("Yes" if dp[X] else "No")
