N, K = map(int, input().split())
(*A,) = map(int, input().split())

# dp[i][j] := j から 2^i 回移動した時の到達点
# dp[i+1][j] = dp[i][dp[i][j]]
dp = [[0] * N for _ in range(61)]
for j in range(N):
    dp[0][j] = A[j] - 1

for i in range(60):
    for j in range(N):
        dp[i + 1][j] = dp[i][dp[i][j]]

cur = 0
for i in range(61):
    if K & (1 << i):
        cur = dp[i][cur]

print(cur + 1)
