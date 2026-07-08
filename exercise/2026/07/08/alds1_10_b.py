N = int(input())

cc = []
for i in range(N):
    r, c = map(int, input().split())
    if i == 0:
        cc.append(r)
    cc.append(c)

INF = 10**18
dp = [[INF] * N for _ in range(N)]
for i in range(N):
    dp[i][i] = 0

for d in range(1, N):
    # d: 区間の長さ
    for l in range(N):
        r = l + d
        if r >= N:
            break

        for k in range(l, r):
            dp[l][r] = min(
                dp[l][r], dp[l][k] + dp[k + 1][r] + cc[l] * cc[k + 1] * cc[r + 1]
            )

print(dp[0][N - 1])
