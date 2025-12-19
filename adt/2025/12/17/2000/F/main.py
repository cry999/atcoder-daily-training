import sys

sys.setrecursionlimit(10**7)


N, X, Y = map(int, input().split())

g = [[] for _ in range(N)]

for _ in range(N-1):
    U, V = map(int, input().split())
    g[U-1].append(V-1)
    g[V-1].append(U-1)

visited = [False]*N


def dfs(u: int) -> list[int]:
    if visited[u]:
        return []
    visited[u] = True

    if u == X-1:
        return [X]

    for v in g[u]:
        if visited[v]:
            continue

        path_to_y = dfs(v)
        if path_to_y:
            path_to_y.append(u+1)
            return path_to_y
    return []


print(*dfs(Y-1))
