N, K, D = map(int, input().split())
(*a,) = map(int, input().split())

# dp[i][d][k] := i 番目までの処遇を決めて、k 個を利用した総和が D で割ったあまりが d の時の最大値
dp = [[[-float("inf")] * D for _ in range(K + 1)] for _ in range(N + 1)]
dp[0][0][0] = 0

for i in range(N):
    for d in range(D):
        for k in range(K + 1):
            # a[i] を利用しない
            dp[i + 1][k][d] = max(dp[i + 1][k][d], dp[i][k][d])
            if k + 1 <= K:
                # a[i] を利用する
                dp[i + 1][k + 1][(a[i] + d) % D] = max(
                    dp[i + 1][k + 1][(a[i] + d) % D],
                    dp[i][k][d] + a[i],
                )

print(max(dp[N][K][0], -1))
