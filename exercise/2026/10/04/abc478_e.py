# >>> atcoder-stat >>>
# started_at  = 2026-10-04T09:34:46+09:00
# solved_at   = 2026-10-04T09:39:45+09:00
# duration_ms = 299719
# ac          = true
# editorial   = true
# knowledge   = 2
# translation = 3
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
from atcoder.scc import SCCGraph
import sys

input = sys.stdin.readline


N, Q = map(int, input().split())
scc = SCCGraph(N)
edges = []
for _ in range(Q):
    t, u, v = map(int, input().split())
    u -= 1
    v -= 1
    scc.add_edge(u, v)
    if t:
        edges.append((u, v))

ans = [0] * N
for i, c in enumerate(scc.scc()):
    for x in c:
        ans[x] = i + 1

if any(ans[u] == ans[v] for u, v in edges):
    print("No")
else:
    print("Yes")
    print(*ans)
