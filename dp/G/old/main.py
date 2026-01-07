import sys

sys.setrecursionlimit(10**7)


N, M = map(int, input().split())
graph = [[] for _ in range(N + 1)]
# in_dim: 各頂点の入次数
in_dim = [0] * (N + 1)

for _ in range(M):
    x, y = map(int, input().split())
    graph[x].append(y)
    in_dim[y] += 1

queue = []
for i in range(N + 1):
    if in_dim[i] == 0:
        queue.append(i)


dist = [0] * (N + 1)


def dfs(u: int):
    global dist

    if dist[u]:
        return dist[u]
    if not graph[u]:
        dist[u] = 1
        return 1

    for v in graph[u]:
        dist[u] = max(dist[u], dfs(v) + 1)
    return dist[u]


print(max(dfs(u) for u in queue) - 1)
