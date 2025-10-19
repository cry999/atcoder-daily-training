import sys


sys.setrecursionlimit(10**7)

N, T = map(int, input().split())
tree = [[] for _ in range(N+1)]

for _ in range(N-1):
    A, B = map(int, input().split())
    tree[A].append(B)
    tree[B].append(A)

ranks = [0] * (N+1)


def dfs(v: int, prev: int) -> int:
    for u in tree[v]:
        if u == prev:
            continue
        ranks[v] = max(ranks[v], dfs(u, v)+1)
    return ranks[v]


dfs(T, -1)

print(*ranks[1:])
