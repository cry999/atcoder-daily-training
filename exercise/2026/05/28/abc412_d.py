N, M = map(int, input().split())
edges = set()

for _ in range(M):
    a, b = map(int, input().split())
    a, b = min(a, b), max(a, b)
    edges.add((a - 1, b - 1))


def dfs(u: int, g: list[list[int]]):
    """全ての頂点が次数 2 のグラフを DFS で全探索する"""
    if u == N:
        e = set()
        for i in range(N):
            for j in g[i]:
                e.add((min(i, j), max(i, j)))

        return len(e.difference(edges) | edges.difference(e))

    ans = float("inf")
    if len(g[u]) == 2:
        ans = min(ans, dfs(u + 1, g))
    elif len(g[u]) == 1:
        for v in range(u + 1, N):
            if len(g[v]) == 2:
                continue
            g[u].append(v)
            g[v].append(u)
            ans = min(ans, dfs(u + 1, g))
            g[u].pop()
            g[v].pop()
    else:  # len(g[u]) == 0
        for v1 in range(u + 1, N):
            if len(g[v1]) == 2:
                continue
            for v2 in range(v1 + 1, N):
                if len(g[v2]) == 2:
                    continue
                g[u].append(v1)
                g[u].append(v2)
                g[v1].append(u)
                g[v2].append(u)
                ans = min(ans, dfs(u + 1, g))
                g[u].pop()
                g[u].pop()
                g[v1].pop()
                g[v2].pop()

    return ans


print(dfs(0, [[] for _ in range(N)]))
