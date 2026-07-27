# >>> atcoder-stat >>>
# started_at  = 2026-07-25T18:45:15+09:00
# solved_at   = 2026-07-25T18:52:49+09:00
# duration_ms = 454232
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


N = int(input())

parts = [tuple(map(int, input().split())) for _ in range(N)]
total_weight = sum(p[0] for p in parts)

M = total_weight // 2

INF = 10**18
# 頭の部品の重さが全体の重さの半分以下で最大の価値を探す。
# dp[w] :=  頭の重さが w で最大の価値
dp = [-INF] * (M + 1)
dp[0] = sum(p[2] for p in parts)

for w, h, b in parts:
    dp[:] = [
        max(dp[u], dp[u - w] + h - b) if u - w >= 0 else dp[u] for u in range(M + 1)
    ]

print(max(dp))
