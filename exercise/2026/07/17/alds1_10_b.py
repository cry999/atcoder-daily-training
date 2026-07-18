N = int(input())
cols = []
for _ in range(N):
    r, c = map(int, input().split())
    if not cols:
        cols.append(r)
    cols.append(c)

INF = 10**18
# dp[l][r] := M_l x M_{l+1} x ... x M_{r} をの積を求めるときのスカラー乗算回数の最小値
dp = [[INF] * N for _ in range(N)]

for i in range(N):
    dp[i][i] = 0

for d in range(1, N):
    for l in range(N - d):
        r = l + d

        for k in range(l, r):
            dp[l][r] = min(
                dp[l][r], dp[l][k] + dp[k + 1][r] + cols[l] * cols[k + 1] * cols[r + 1]
            )
print(dp[0][N - 1])
