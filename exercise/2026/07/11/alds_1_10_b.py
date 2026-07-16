N = int(input())
cols = []
for i in range(N):
    r, c = map(int, input().split())
    if i == 0:
        cols.append(r)
    cols.append(c)

INF = 10**18
dp = [[INF] * (N + 1) for _ in range(N + 1)]
for i in range(N):
    dp[i][i + 1] = 0

for d in range(2, N + 1):
    for l in range(N):
        r = l + d
        if r > N:
            break

        for k in range(l + 1, r):
            dp[l][r] = min(dp[l][r], dp[l][k] + dp[k][r] + cols[l] * cols[k] * cols[r])
print(dp[0][N])
