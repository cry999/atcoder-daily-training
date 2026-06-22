import sys

sys.setrecursionlimit(10**7)

N = int(input())
g = [[] for _ in range(N + 1)]
color = [-1] * (N - 1)

for i in range(N - 1):
    a, b = map(int, input().split())
    a, b = a - 1, b - 1
    g[a].append((b, i))
    g[b].append((a, i))


def dfs(u: int, p: int = -1, c: int = -1):
    """
    u: 現在の頂点
    p: u の親
    c: くる時に使った辺 (u と親をつなぐ辺) の色
    """
    k = 1
    for v, i in g[u]:
        if v == p:
            continue
        if k == c:
            k += 1

        color[i] = k
        dfs(v, u, k)

        k += 1


dfs(0)

print(max(color))
for c in color:
    print(c)
