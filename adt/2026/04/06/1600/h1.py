import sys

sys.setrecursionlimit(10**7)

N = int(input())
tree = [[] for _ in range(N + 1)]

for _ in range(N - 1):
    u, v = map(int, input().split())
    tree[u].append(v)
    tree[v].append(u)

L = [-1] * (N + 1)
R = [-1] * (N + 1)


def dfs(u: int, n: int = 1, p: int = -1):
    L[u] = n
    R[u] = n

    for v in tree[u]:
        if v == p:
            continue
        R[u] = dfs(v, n, u)
        n = R[u] + 1

    return R[u]


dfs(1)
# print(L)
# print(R)
for l, r in zip(L[1:], R[1:]):
    print(l, r)
