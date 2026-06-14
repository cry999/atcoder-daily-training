MOD = 998244353
N = int(input())

(*A,) = map(int, input().split())
(*B,) = map(int, input().split())

M = max(B)

# dp[i][j] := C[i] を j とする C 以下とするあり得る数列の個数
dp = [[0] * (M + 1) for _ in range(N + 1)]
for j in range(M + 1):
    dp[0][j] = 1

for i in range(N):
    for j in range(M + 1):
        if max(A[i], j) <= j <= B[i]:
            dp[i + 1][j] += dp[i][j]
        if j - 1 >= 0:
            dp[i + 1][j] += dp[i + 1][j - 1]
        dp[i + 1][j] %= MOD

print(dp[N][M])
