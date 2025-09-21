N, M = map(int, input().split())
A = [0] + [
    int(''.join(input().split()), 2)
    for _ in range(M)
]

# dp[i][j] := i 番目までのチケットを利用して、j が表す品物を購入するためのクーポンの最小値
# j は 2 進数表示した時に、1 の部分が該当する品物を買うことに相当する。
dp = [[float('inf')] * (1 << N) for _ in range(M+1)]
dp[0][0] = 0

for i in range(1, M+1):
    dp[i][0] = 0
    for j in range(1 << N):
        dp[i][j] = min(dp[i][j], dp[i-1][j])
        dp[i][j | A[i]] = min(dp[i][j | A[i]], dp[i-1][j] + 1)

# for i in range(1 << N):
#     print(bin(i))
print(dp[M][(1 << N) - 1] if dp[M][(1 << N) - 1] != float('inf') else -1)
