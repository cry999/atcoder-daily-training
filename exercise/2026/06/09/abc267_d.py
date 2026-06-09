N, M = map(int, input().split())
(*A,) = map(int, input().split())

# dp[n][m] := A[1] ~ A[n] から m こ選ぶ時の sum(i x B[i]) の最大値
dp = [[-float("inf")] * (M + 1) for _ in range(N + 1)]
dp[0][0] = 0

for i in range(N):
    for m in range(min(i + 1, M) + 1):
        dp[i + 1][m] = max(
            dp[i + 1][m],
            dp[i][m - 1] + m * A[i] if m > 0 else 0,
            dp[i][m],  # 選ばない場合
        )
print(dp[N][M])
# print("[DEBUG]", dp)
