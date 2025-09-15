N, W = map(int, input().split())
V = 1000

# dp[i][v] := i番目まで見たときに価値の総和がvとなるような重さの最小値
dp = [[float('inf')] * (N*V+1) for _ in range(N+1)]
dp[0][0] = 0

for i in range(N):
    wi, vi = map(int, input().split())
    for v in range(N*V+1):
        if v - vi >= 0:
            dp[i+1][v] = min(dp[i][v], dp[i][v-vi] + wi)
        else:
            dp[i+1][v] = dp[i][v]

for v in range(N*V, -1, -1):
    if dp[N][v] <= W:
        print(v)
        break
