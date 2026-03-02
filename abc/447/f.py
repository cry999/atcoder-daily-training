import sys

sys.setrecursionlimit(10**7)


Q = int(input())


for _ in range(Q):
    N = int(input())
    g = [[] for _ in range(N + 1)]
    deg = [0] * (N + 1)
    dp = [-1] * (N + 1)

    for _ in range(N - 1):
        a, b = map(int, input().split())
        g[a].append(b)
        g[b].append(a)
        deg[a] += 1
        deg[b] += 1

    ans = 1

    def dfs(u: int, p: int) -> int:
        global ans
        dp = sorted([dfs(v, u) for v in g[u] if v != p], reverse=True)

        up = 0
        if deg[u] >= 4:
            up = dp[0] + 1
            ans = max(ans, dp[0] + dp[1] + 1)
        elif deg[u] == 3:
            up = 1
            ans = max(ans, dp[0] + 1)
        return up

    dfs(1, -1)
    print(ans)
