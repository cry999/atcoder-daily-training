N, K, D = map(int, input().split())
(*a,) = map(int, input().split())

dp = [[[-float("inf")] * D for _ in range(K + 1)] for _ in range(N + 1)]
dp[0][0][0] = 0

for n in range(N):
    for k in range(min(n + 1, K) + 1):
        for d in range(D):
            dp[n + 1][k][d] = max(
                dp[n][k][d],
                (dp[n][k - 1][(d - a[n]) % D] + a[n]) if k > 0 else -float("inf"),
            )

ans = dp[-1][-1][0]
if ans >= 0:
    print(ans)
else:
    print(-1)
