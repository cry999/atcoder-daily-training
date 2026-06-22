MOD = 10**9 + 7

S = input()
N = len(S)

dp = [[0] * 13 for _ in range(N + 1)]
dp[0][0] = 1

pow10 = 1
for i in range(N):
    s = S[N - i - 1]
    if s == "?":
        for j in range(10):
            for d in range(13):
                dp[i + 1][(j * pow10 + d) % 13] += dp[i][d]
                dp[i + 1][(j * pow10 + d) % 13] %= MOD
    else:
        j = int(s)
        for d in range(13):
            dp[i + 1][(j * pow10 + d) % 13] += dp[i][d]
            dp[i + 1][(j * pow10 + d) % 13] %= MOD

    pow10 = (pow10 * 10) % 13

print(dp[N][5])
