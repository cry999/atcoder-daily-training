X, Y, Z = map(int, input().split())
S = input()
N = len(S)

ON = 1
OFF = 0
dp = [[0] * 2 for _ in range(N + 1)]
dp[0][ON] = Z

for i, s in enumerate(S):
    if s == "a":
        dp[i + 1][ON] = min(
            dp[i][ON] + Y,  # ON なので、shift + a キー
            dp[i][OFF] + X + Z,
        )
        dp[i + 1][OFF] = min(
            dp[i][OFF] + X,  # OFF なので a キー
            dp[i][ON] + Y + Z,
        )
    else:
        dp[i + 1][ON] = min(
            dp[i][ON] + X,  # ON なので、 a キー
            dp[i][OFF] + Y + Z,
        )
        dp[i + 1][OFF] = min(
            dp[i][OFF] + Y,  # OFF なので shift + a キー
            dp[i][ON] + X + Z,
        )

print(min(dp[N]))
