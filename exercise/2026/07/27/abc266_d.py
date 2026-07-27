# >>> atcoder-stat >>>
# started_at  = 2026-07-27T21:53:55+09:00
# solved_at   = 2026-07-27T22:04:31+09:00
# duration_ms = 636743
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())

INF = float("inf")
# dp[i] := 高橋くんが穴 i にいる時の最大スコア
dp = [-INF] * 5
dp[0] = 0

current_time = 0
for _ in range(N):
    t, x, a = map(int, input().split())

    dt = t - current_time
    print(f"[DEBUG] {dp=}")
    print(f"[DEBUG] {dt=}: {dp[max(0, x-dt):min(5, x+dt+1)]=}")
    dp = [max(dp[max(0, i - dt) : min(5, i + dt + 1)]) for i in range(5)]
    dp[x] += a
    current_time = t

print(max(dp))
