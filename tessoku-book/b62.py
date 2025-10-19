import sys


sys.setrecursionlimit(10**6)

N, M = map(int, input().split())
nodes = [[] for _ in range(N+1)]

for _ in range(M):
    A, B = map(int, input().split())
    nodes[A].append(B)
    nodes[B].append(A)

visited = [False] * (N+1)


def dfs(v: int) -> list[int]:
    if v == 1:
        return [1]

    for next in nodes[v]:
        if visited[next]:
            continue

        visited[next] = True
        ret = dfs(next)
        if ret:
            ret.append(v)
            return ret
    return []


print(*dfs(N))
