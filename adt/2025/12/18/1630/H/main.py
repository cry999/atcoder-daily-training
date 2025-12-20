import sys
import os

DEBUG = os.environ.get("DEBUG", "0") == "1"


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs, file=sys.stderr)


N = int(input())

g = [[] for _ in range(N)]

for _ in range(N-1):
    u, v = map(int, input().split())
    g[u-1].append(v-1)
    g[v-1].append(u-1)

ans = float('inf')
for u in range(N):
    debug(f'node {u+1}:')
    dims = []
    for v in g[u]:
        dims.append(len(g[v])-1)
    dims.sort(reverse=True)

    # debug(f'  {dims=}')
    for x, y in enumerate(dims):
        debug(f'  {x+1=}, {y=}, {1+(x+1)+(x+1)*y=}')
        ans = min(ans, N-(1+(x+1)+(x+1)*y))
print(ans)
