N = int(input())
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())
(*C,) = map(int, input().split())

# dp[i][j] := i 番目まで処理した時に A, B, C が末尾となる時の最大値
# j = 0 -> A, j = 1 -> B, j = 2 -> C
dp = [[0] * 3 for _ in range(N)]
dp[0][0] = A[0]

for i in range(1, N):
    dp[i][0] = dp[i - 1][0] + A[i]
    dp[i][1] = dp[i - 1][0] + B[i]

    if dp[i - 1][1] > 0:
        dp[i][1] = max(dp[i][1], dp[i - 1][1] + B[i])
        dp[i][2] = dp[i - 1][1] + C[i]
    if dp[i - 1][2] > 0:
        dp[i][2] = max(dp[i][2], dp[i - 1][2] + C[i])

print(dp[N - 1][2])
