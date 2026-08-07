# >>> atcoder-stat >>>
# started_at  = 2026-08-07T14:26:34+09:00
# solved_at   = 2026-08-07T14:37:33+09:00
# duration_ms = 659330
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<

N = int(input())
M = 10**5
INF = float("inf")
dp = [INF] * (M + 1)
dp[0] = 0

total_z = 0
for _ in range(N):
    x, y, z = map(int, input().split())
    cost = max(0, (y - x + 1) // 2)
    total_z += z

    for seat in range(M, z - 1, -1):
        dp[seat] = min(dp[seat], dp[seat - z] + cost)

ans = min(dp[seat] for seat in range((total_z + 1) // 2, M + 1))
print(ans)
