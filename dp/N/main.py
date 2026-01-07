import sys

sys.setrecursionlimit(10**7)


N = int(input())
(*a,) = map(int, input().split())

dp = [[-1] * (N + 1) for _ in range(N + 1)]
c = [0] * (N + 1)
for i in range(N):
    c[i + 1] = c[i] + a[i]


def dfs(l: int, r: int) -> int:
    if r < l:
        return float("inf")

    if dp[l][r] != -1:
        return dp[l][r]

    if r == l:
        dp[l][r] = 0
        return dp[l][r]

    if r == l + 1:
        dp[l][r] = a[l] + a[r]
        return dp[l][r]

    dp[l][r] = float("inf")
    for i in range(l, r):
        dp[l][r] = min(dp[l][r], dfs(l, i) + dfs(i + 1, r))
    dp[l][r] += c[r + 1] - c[l]
    return dp[l][r]


print(dfs(0, N - 1))
