# >>> atcoder-stat >>>
# started_at  = 2026-07-22T16:29:09+09:00
# <<< atcoder-stat <<<
N, K = map(int, input().split())
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())

dp = [[0] * 2 for _ in range(N)]
dp[0][0] = 1
dp[0][1] = 1

for i in range(1, N):
    if abs(A[i] - A[i - 1]) <= K:
        dp[i][0] |= dp[i - 1][0]
    if abs(A[i] - B[i - 1]) <= K:
        dp[i][0] |= dp[i - 1][1]
    if abs(B[i] - A[i - 1]) <= K:
        dp[i][1] |= dp[i - 1][0]
    if abs(B[i] - B[i - 1]) <= K:
        dp[i][1] |= dp[i - 1][1]

print("Yes" if sum(dp[-1]) else "No")
