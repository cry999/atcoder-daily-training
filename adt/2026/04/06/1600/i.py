from sys import setrecursionlimit

setrecursionlimit(10**7)

N, M = map(int, input().split())
g = [[] for _ in range(N + 1)]

for _ in range(M):
    u, v = map(int, input().split())
    g[u].append(v)

reach_loop = [False] * (N + 1)
visited = [False] * (N + 1)
finished = [False] * (N + 1)
history = []


def dfs(u: int):
    if reach_loop[u]:
        return u

    visited[u] = True
    history.append(u)

    for v in g[u]:
        if finished[v]:
            continue

        if visited[v] and not finished[v]:
            history.append(v)
            return v

        pos = dfs(v)
        if pos != -1:
            return pos

    finished[u] = True
    history.pop()

    return -1


for i in range(N):
    i += 1

    pos = dfs(i)
    while history:
        u = history.pop()
        reach_loop[u] = True

print(sum(reach_loop))
