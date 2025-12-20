N, X = map(int, input().split())

dp = [[0]*(X+1) for _ in range(2)]
dp[0][0] = 1

for i in range(N):
    a, b = map(int, input().split())
    for x in range(X+1):
        dp[(i+1) % 2][x] = 0
        if x-a >= 0:
            dp[(i+1) % 2][x] += dp[i % 2][x-a]
        if x-b >= 0:
            dp[(i+1) % 2][x] += dp[i % 2][x-b]

print('Yes' if dp[N % 2][X] else 'No')
