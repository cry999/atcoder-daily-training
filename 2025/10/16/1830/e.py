N, X = map(int, input().split())

# dp[n][x] := n 回のジャンプを行った後に x の地点にいるか？
dp = [[False]*(X+1) for _ in range(N+1)]
dp[0][0] = True

for n in range(N):
    a, b = map(int, input().split())
    for x in range(X):
        if not dp[n][x]:
            continue
        if x+a <= X:
            dp[n+1][x+a] = True
        if x+b <= X:
            dp[n+1][x+b] = True

print('YNeos'[not dp[N][X]::2])
