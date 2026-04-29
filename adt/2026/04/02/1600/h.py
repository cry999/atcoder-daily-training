from sys import setrecursionlimit

setrecursionlimit(10**7)


N = int(input())
g = [set() for _ in range(N)]

for _ in range(N - 1):
    u, v = map(lambda x: int(x) - 1, input().split())
    g[u].add(v)
    g[v].add(u)

# N <= 100 なので、log(N) < 10 なので 10 もあればダブリングには十分
parent = [[-1] * N for _ in range(10)]
depth = [-1] * N


# 初期化
def dfs(u: int, par: int = -1, dep: int = 0):
    parent[0][u] = par
    depth[u] = dep

    for v in g[u]:
        if v == par:
            continue
        dfs(v, u, dep + 1)

    return


# root: 0
dfs(0)

for k in range(9):
    for u in range(N):
        if parent[k][u] < 0:
            parent[k + 1][u] = -1
        else:
            parent[k + 1][u] = parent[k][parent[k][u]]


def lca(u: int, v: int) -> int:
    """u と v の LCA (Lowest Common Ancestore) を返す"""
    if depth[u] > depth[v]:
        u, v = v, u

    # u と v を同じ深さまで遡る
    for k in range(10):
        if ((depth[v] - depth[u]) >> k) & 1:
            v = parent[k][v]
    if u == v:
        return u

    for k in range(9, -1, -1):
        if parent[k][u] != parent[k][v]:
            u = parent[k][u]
            v = parent[k][v]

    return parent[0][u]


can_use = []
for u in range(N):
    for v in range(u + 1, N):
        if v in g[u]:
            continue
        par = lca(u, v)
        n = (depth[u] - depth[par]) + (depth[v] - depth[par])
        if n & 1 == 1:
            can_use.append((u, v))

if len(can_use) % 2 == 0:
    print("Second")
else:
    print("First")
    u, v = can_use.pop()
    print(u + 1, v + 1)
    g[u].add(v)
    g[v].add(u)

while can_use:
    a, b = map(lambda x: int(x) - 1, input().split())
    g[a].add(b)
    g[b].add(a)

    while True:
        u, v = can_use.pop()
        if v in g[u]:
            continue
        print(u + 1, v + 1)
        g[u].add(v)
        g[v].add(u)
        break
