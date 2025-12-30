N = int(input())
S = input()
(*C,) = map(int, input().split())

# dp[z][i] := z で始まる 1010 文字列を作るときに i 文字目まで
# の変換でかかるコスト。
dp = [[0] * (N + 1) for _ in range(2)]

for i in range(N):
    s = S[i]
    dp[0][i + 1] += dp[0][i]
    dp[1][i + 1] += dp[1][i]
    if i % 2 == 0:
        # 0 で始まる 1010 文字列は i%2 == 0 を満たす
        # i 文字目は 0 である。
        dp[0][i + 1] += 0 if s == "0" else C[i]
        # 1 で始まる 1010 文字列は i%2 == 1 を満たす
        # i 文字目は 1 である。
        dp[1][i + 1] += 0 if s == "1" else C[i]
    else:
        dp[0][i + 1] += 0 if s == "1" else C[i]
        dp[1][i + 1] += 0 if s == "0" else C[i]


ans = float("inf")
for i in range(N - 1):
    # i 文字目と i+1 文字目を 00 / 11 にして、そのほかを
    # 1010 文字列にすることを考えると、結局は i 文字目を 1010 文字列にして
    # i+1 文字目以降を 0101 文字列にする or i 文字目を 0101 文字列にして
    # i+1 文字目以降を 1010 文字列にするかの 2 通り。
    ans = min(
        ans,
        (dp[0][i + 1] - dp[0][0]) + (dp[1][N] - dp[1][i + 1]),
        (dp[1][i + 1] - dp[1][0]) + (dp[0][N] - dp[0][i + 1]),
    )

print(ans)
