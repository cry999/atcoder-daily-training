N = int(input())
(*a,) = map(int, input().split())

dp = [[-float("inf")] * N for _ in range(N)]

for i in range(N):
    dp[i][i] = a[i]

for d in range(1, N):
    for l in range(N):
        r = l + d
        if r >= N:
            continue
        dp[l][r] = max(
            a[l] - dp[l + 1][r] if l + 1 <= r else 0,
            a[r] - dp[l][r - 1] if l <= r - 1 else 0,
        )
print(dp[0][-1])
