import sys
import os

DEBUG = os.environ.get("DEBUG", "0") == "1"


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs, file=sys.stderr)


sys.setrecursionlimit(10**7)


N, K = map(int, input().split())

g = [[] for _ in range(N)]

for _ in range(N-1):
    a, b = map(int, input().split())
    g[a-1].append(b-1)
    g[b-1].append(a-1)

*V, = map(int, input().split())
root = V[0]-1
set_v = set(v-1 for v in V)

visited = [False]*N


def dfs(u: int) -> int:
    if visited[u]:
        return 0
    visited[u] = True
    debug(f'visiting {u}')

    ans = 0
    for v in g[u]:
        if visited[v]:
            continue
        old = ans
        ans += dfs(v)
        debug(f'  from {u} to {v}: {ans-old}')

    debug(f'  returning from {u} with ans={ans}')
    return ans + (ans > 0 or (u in set_v))


print(dfs(root))
