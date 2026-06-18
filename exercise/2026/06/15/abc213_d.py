import sys

sys.setrecursionlimit(10**7)
input = sys.stdin.readline


N = int(input())
g = [[] for _ in range(N + 1)]

for _ in range(N - 1):
    u, v = map(int, input().split())
    g[u].append(v)
    g[v].append(u)

for u in range(1, N + 1):
    g[u].sort()

ans = []


def dfs(u: int, p: int = -1):
    ans.append(u)
    for v in g[u]:
        if v == p:
            continue
        dfs(v, u)
        ans.append(u)
    return


dfs(1)

print(*ans)
