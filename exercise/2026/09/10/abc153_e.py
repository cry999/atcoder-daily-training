# >>> atcoder-stat >>>
# started_at  = 2026-09-10T10:57:49+09:00
# solved_at   = 2026-09-10T11:11:39+09:00
# duration_ms = 830328
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


H, N = map(int, input().split())

INF = 10**18
# dp[h] = ダメージが h になる最小の魔力
dp = [INF] * (H + 1)
dp[0] = 0

for _ in range(N):
    a, b = map(int, input().split())
    for h in range(H):
        nxt = min(H, h + a)
        dp[nxt] = min(dp[nxt], dp[h] + b)
print(dp[H])
