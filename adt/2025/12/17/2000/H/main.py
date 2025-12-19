import sys


sys.setrecursionlimit(10**7)


N = int(input())
*x, = map(int, input().split())

g = [[] for _ in range(N)]
for _ in range(N-1):
    u, v, w = map(int, input().split())
    g[u-1].append((v-1, w))
    g[v-1].append((u-1, w))


def dfs(u: int, par: int) -> int:
    ans = 0
    for v, w in g[u]:
        if v == par:
            continue
        ans += dfs(v, u)
        ans += abs(x[v]) * w
        x[u] += x[v]
        x[v] = 0
    return ans


print(dfs(0, -1))
