import sys

sys.setrecursionlimit(10**7)

N, K = map(int, input().split())
g = [[] for _ in range(N)]

for _ in range(N - 1):
    a, b = map(int, input().split())
    a -= 1
    b -= 1
    g[a].append(b)
    g[b].append(a)

(*V,) = map(int, input().split())
need = [False] * N
for v in V:
    need[v - 1] = True


def dfs(u: int, p: int = -1) -> int:
    node_num = 0
    for v in g[u]:
        if v == p:
            continue
        node_num += dfs(v, u)
    if need[u] or node_num > 0:
        node_num += 1
    return node_num


print(dfs(V[0] - 1))
