N = int(input())
(*a,) = map(int, input().split())

# dp[l][r] := [l, r] の範囲の数字が残っている時に手番が回ってきた方から
# みた、得点差の最大値
dp = [[float("inf")] * N for _ in range(N)]
for i in range(N):
    dp[i][i] = a[i]

for d in range(1, N):
    for l in range(N - d):
        r = l + d
        dp[l][r] = max(a[l] - dp[l + 1][r], a[r] - dp[l][r - 1])

print(dp[0][-1])
