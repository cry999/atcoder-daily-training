# >>> atcoder-stat >>>
# started_at  = 2026-09-10T11:13:49+09:00
# solved_at   = 2026-09-10T11:25:41+09:00
# duration_ms = 712712
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, K, P = map(int, input().split())

INF = 10**18

dp = {}
dp[(0,) * K] = 0

for _ in range(N):
    c, *a = map(int, input().split())

    for k, v in list(dp.items()):
        nk = tuple(min(P, k[i] + a[i]) for i in range(K))
        dp[nk] = min(dp.get(nk, INF), v + c)

goal = (P,) * K
if goal in dp:
    print(dp[goal])
else:
    print(-1)
