N = int(input())
(*a,) = map(int, input().split())

dp = [[float("inf")] * N for _ in range(N)]
cum = [0] * (N + 1)
for i in range(N):
    cum[i + 1] = cum[i] + a[i]


def dfs(l: int, r: int):
    if l > r:
        return float("inf")
    if l == r:
        return 0
    if dp[l][r] != float("inf"):
        return dp[l][r]
    if r - l == 1:
        dp[l][r] = a[l] + a[r]
        return dp[l][r]

    for m in range(l, r):
        dp[l][r] = min(dp[l][r], dfs(l, m) + dfs(m + 1, r) + cum[r + 1] - cum[l])
    return dp[l][r]


print(dfs(0, N - 1))
