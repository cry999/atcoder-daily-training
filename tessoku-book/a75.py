N = int(input())
tasks = [tuple(map(int, input().split())) for _ in range(N)]
tasks.sort(key=lambda x: x[1])

_, max_deadline = max(tasks, key=lambda x: x[1])

# dp[i][j]: i 番目までの仕事までの仕事が終わった時点で現在時刻が j であるときの
# 最大消化数
dp = [[0] * (max_deadline+1) for _ in range(N+1)]

for i, (time, deadline) in enumerate(tasks):
    for j in range(max_deadline+1):
        if j < time:
            dp[i+1][j] = dp[i][j]
        elif j <= deadline:
            dp[i+1][j] = max(dp[i][j], dp[i][j-time]+1)
        else:
            dp[i+1][j] = dp[i][j]

# print(dp)
print(max(dp[N]))
