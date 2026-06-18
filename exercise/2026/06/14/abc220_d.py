MOD = 998244353


N = int(input())
(*A,) = map(int, input().split())

dp = [[0] * 10 for _ in range(N)]
dp[0][A[0]] = 1

for i in range(N - 1):
    x = A[i + 1]
    for k in range(10):
        dp[i + 1][(x + k) % 10] += dp[i][k]
        dp[i + 1][(x + k) % 10] %= MOD

        dp[i + 1][(x * k) % 10] += dp[i][k]
        dp[i + 1][(x * k) % 10] %= MOD

for ans in dp[N - 1]:
    print(ans)
