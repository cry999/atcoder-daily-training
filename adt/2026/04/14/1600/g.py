from collections import defaultdict
import sys

sys.setrecursionlimit(10**7)


N = int(input())
(*A,) = map(int, input().split())
g = [[] for _ in range(N)]

for _ in range(N - 1):
    u, v = map(lambda x: int(x) - 1, input().split())
    g[u].append(v)
    g[v].append(u)

ans = [False] * N
hist = defaultdict(int)


def dfs(u: int, p: int = -1, dup: bool = False):
    hist[A[u]] += 1
    ans[u] = dup or hist[A[u]] > 1
    for v in g[u]:
        if v == p:
            continue
        dfs(v, u, ans[u])

    hist[A[u]] -= 1


dfs(0)

for a in ans:
    print("Yes" if a else "No")
