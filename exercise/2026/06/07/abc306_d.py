N = int(input())

FINE = 0
POISON = 1

dp = [[-float("inf")] * 2 for _ in range(N + 1)]
dp[0][FINE] = 0

for i in range(N):
    x, y = map(int, input().split())

    if x == 0:  # 解毒入り
        dp[i + 1][FINE] = max(
            dp[i][FINE] + y,
            dp[i][FINE],  # 下げてもらう
            dp[i][POISON] + y,
        )
        dp[i + 1][POISON] = dp[i][POISON]  # 下げてもらう
    else:  # 毒入り
        dp[i + 1][FINE] = dp[i][FINE]  # 下げてもらう
        dp[i + 1][POISON] = max(
            dp[i][FINE] + y,
            dp[i][POISON],  # 下げてもらう
        )

print(max(dp[N]))
