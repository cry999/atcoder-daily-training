N = int(input())
MOD = 10**9 + 7

(*a,) = [list(map(int, input().split())) for _ in range(N)]

# dp[i][j]: i 番目の男性までをマッチングできるか判断した時の女性のマッチング状況が j である場合の数
dp = [[0] * (1 << N) for _ in range(N + 1)]
dp[0][0] = 1

for i in range(N):
    for j in range(1 << N):
        if dp[i][j] == 0:
            continue

        for k in range(N):
            if j & (1 << k):
                continue
            if a[i][k] == 0:
                continue
            dp[i + 1][j | (1 << k)] += dp[i][j]
            dp[i + 1][j | (1 << k)] %= MOD

print(dp[-1][-1])
