MOD = 998244353


N = int(input())

cards = [tuple(map(int, input().split())) for _ in range(N)]

FRONT = 0
BACK = 1
dp = [[0] * 2 for _ in range(N)]
dp[0][FRONT] = dp[0][BACK] = 1

for i in range(N - 1):
    for j in range(2):
        for k in range(2):
            if cards[i + 1][j] != cards[i][k]:
                dp[i + 1][j] += dp[i][k]
                dp[i + 1][j] %= MOD

print(sum(dp[N - 1]) % MOD)
