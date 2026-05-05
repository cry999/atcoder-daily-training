MOD = 998244353

N = int(input())
(*a,) = map(int, input().split())

ans = 0
for k in range(N):
    k += 1
    # k 個の平均を計算する。
    # dp[i][j][n] := a[i] までの内 j 個を利用した和を k で割ったあまりが n である個数
    dp = [[[0] * k for _ in range(k + 1)] for _ in range(N + 1)]
    dp[0][0][0] = 1

    for i in range(N):
        for j in range(k + 1):
            for d in range(k):
                dp[i + 1][j][d] += dp[i][j][d]
                dp[i + 1][j][d] %= MOD

            if j == k:
                break

            for d in range(k):
                dp[i + 1][j + 1][(d + a[i]) % k] += dp[i][j][d]
                dp[i + 1][j + 1][(d + a[i]) % k] %= MOD

    # print(dp[N][k][0])
    ans += dp[N][k][0]
    ans %= MOD

print(ans)
