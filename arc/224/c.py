import sys

sys.setrecursionlimit(10**6)
T = int(input())

for _ in range(T):
    N, M = map(int, input().split())
    g = [[] for _ in range(N)]

    for _ in range(M):
        u, v = map(int, input().split())
        g[u - 1].append(v - 1)
        g[v - 1].append(u - 1)

    q = [(0, 0)]
    ans = [-1] * N

    def dfs(u: int, p: int = -1, d: int = 0):
        ans[u] = d

        for v in g[u]:
            if v == p:
                continue
            if ans[v] != -1:
                continue
            dfs(v, u, d + 1)

    dfs(0)
    print(*ans)
