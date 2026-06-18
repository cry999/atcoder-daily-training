N, M = map(int, input().split())
g = [[] for _ in range(N + 1)]

for _ in range(M):
    a, b = map(int, input().split())

    g[a].append(b)
    g[b].append(a)

visited = [False] * (N + 1)
dag = [[] for _ in range(N + 1)]


def dfs_to_dag(u: int):
    if visited[u]:
        return
    visited[u] = True

    for v in g[u]:
        if visited[v]:
            continue
        dag[u].append(v)
        dfs_to_dag(v)


for u in range(1, N + 1):
    if visited[u]:
        continue
    dfs_to_dag(u)

color = [-1] * (N + 1)
visited = [False] * (N + 1)


def dfs(u: int, d: int = 0):
    visited[u] = True
    res = 0
    for c in range(3):
        # 色の確認は DAG ではなく元のグラフで行う
        if any(color[v] == c for v in g[u]):
            continue

        color[u] = c

        t = 1
        for v in dag[u]:
            if color[v] != -1:
                continue
            t *= dfs(v, d + 1)
        res += t
    color[u] = -1
    return res


ans = 1
for u in range(1, N + 1):
    if visited[u]:
        continue
    ans *= dfs(u)
print(ans)
