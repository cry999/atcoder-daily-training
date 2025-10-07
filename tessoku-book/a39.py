N = int(input())
# movies[R] = L
movies = {}
# dp[i]: 時刻 i までに見た映画の最大本数
dp = [0] * (86400+1)

for _ in range(N):
    L, R = map(int, input().split())
    movies[R] = movies.get(R, []) + [L]

for i in range(1, 86400+1):
    dp[i] = dp[i-1]
    for L in movies.get(i, []):
        dp[i] = max(dp[i], dp[L] + 1)

print(dp[86400])
