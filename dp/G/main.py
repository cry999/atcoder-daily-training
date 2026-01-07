import sys

sys.setrecursionlimit(10**7)


N, M = map(int, input().split())
tree = [[] for _ in range(N + 1)]

for _ in range(M):
    x, y = map(int, input().split())
    tree[x].append(y)

dp = [-1] * (N + 1)


def dfs(u: int) -> int:
    global tree, dp

    if dp[u] >= 0:
        return dp[u]

    dp[u] = 0
    for v in tree[u]:
        dp[u] = max(dp[u], dfs(v) + 1)
    return dp[u]


ans = 0
for i in range(N + 1):
    if dp[i] >= 0:
        continue

    ans = max(ans, dfs(i))

print(ans)
