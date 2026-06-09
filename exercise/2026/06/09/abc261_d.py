N, M = map(int, input().split())
(*X,) = map(int, input().split())
bonus = [0] * (N + 1)
for _ in range(M):
    C, Y = map(int, input().split())
    bonus[C] = Y

# dp[n][c] := n 回目のゲームで、カウンタが c (<=n) の時の最大スコア
dp = [[0] * (N + 1) for _ in range(N + 1)]
for n in range(N):
    for c in range(n + 1):
        # 表
        if c <= n:
            dp[n + 1][c + 1] = max(dp[n + 1][c + 1], dp[n][c] + X[n] + bonus[c + 1])
        # 裏
        dp[n + 1][0] = max(dp[n + 1][0], dp[n][c])

print(max(dp[N]))
