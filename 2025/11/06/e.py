N, K, T = map(int, input().split())
*P, = map(int, input().split())

# s: 濡れる量
s = sum(P[:T])
# nureru[i]: 時刻 i から i+T までに濡れる量
nureru = [0] * (N-T+1)
nureru[0] = s
for i in range(1, N-T+1):
    s = s - P[i-1] + P[i+T-1]
    nureru[i] = s


# dp[k][i]: k 回アトラクションに乗車して時刻 i になった場合の濡れる量の最小値
dp = [[float('inf')] * (N+1) for _ in range(K+1)]
dp[0] = [0] * (N+1)

for k in range(K):
    for i, p in enumerate(nureru):
        dp[k+1][i+T] = min(dp[k+1][i+T], dp[k+1][i+T-1], dp[k][i] + p)
print(dp[K][N])
# print(dp)
