# >>> atcoder-stat >>>
# started_at  = 2026-07-22T16:18:47+09:00
# solved_at   = 2026-07-22T16:28:59+09:00
# duration_ms = 612955
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, M = map(int, input().split())
dp = [[] for _ in range(N + 1)]
dp[0].append([0])

for i in range(N):
    for a in dp[i]:
        for n in range(a[-1] + 1, M - N + i + 2):
            dp[i + 1].append(a[:] + [n])

for a in dp[N]:
    print(*a[1:])
