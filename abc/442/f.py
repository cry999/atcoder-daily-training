N = int(input())
S = [input() for _ in range(N)]

# whites[i][j]: i 行目の左から j 個目のマスの左に白と黒の境目をおくときに、境目の右側にある白の個数
whites = [[0] * (N + 1) for _ in range(N)]
# blacks[i][j]: i 行目の左から j 個目のマスの左に白と黒の境目をおくときに、境目の左側にある黒の個数
blacks = [[0] * (N + 1) for _ in range(N)]
# whites[i][ki] + blacks[i][ki] が i 行目の ki に境目を引いた時に必要な操作の回数
for i in range(N):
    for j in range(N):
        whites[i][N - j - 1] = whites[i][N - j] + (S[i][N - j - 1] == ".")
        blacks[i][j + 1] = blacks[i][j] + (S[i][j] == "#")

# print(whites)
# print(blacks)

# dp[i][j] := i 行目の j 番目より右に境目を置いた場合の操作の最小値
dp = [[float("inf")] * (N + 1) for _ in range(N + 1)]
for i in range(N + 1):
    dp[0][i] = 0

for i in range(N):
    for k in range(N, -1, -1):
        dp[i + 1][k] = dp[i][k] + whites[i][k] + blacks[i][k]
        if k + 1 <= N:
            dp[i + 1][k] = min(dp[i + 1][k], dp[i + 1][k + 1])

print(dp[-1][0])
