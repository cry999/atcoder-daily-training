from sys import setrecursionlimit

setrecursionlimit(10**7)


N = int(input())
g = [[] for _ in range(N)]

for _ in range(N - 1):
    u, v = map(lambda x: int(x) - 1, input().split())
    g[u].append(v)
    g[v].append(u)

ans = [(0, 0)] * N


def dfs(u: int, l: int = 1, p: int = -1) -> int:
    # print(f"dfs({u}, {l}, {p})")
    r = l
    for v in g[u]:
        if v == p:
            continue
        r = dfs(v, r, u)
        r += 1
    ans[u] = (l, max(l, r - 1))
    # print(f"ans[{u}] = {ans[u]}")
    return max(l, r - 1)


dfs(0)
for l, r in ans:
    print(l, r)
