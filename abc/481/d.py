import heapq
import sys
from sortedcontainers import SortedSet

input = sys.stdin.readline


N, M, S, T = map(int, input().split())
g: list[SortedSet[int]] = [SortedSet() for _ in range(N + 1)]

for _ in range(M):
    a, b = map(int, input().split())
    g[a].add(b)


q = [(0, S)]
INF = 10**18
dist = [INF] * (N + 1)
dist[S] = 0
while q:
    c, u = heapq.heappop(q)
    # print(f"[DEBUG] visit {u=} @ {c=}")
    for i, v in enumerate(g[u]):
        cost = 0 if i == 0 else 1
        next_cost = cost + c
        if dist[v] <= next_cost:
            continue
        dist[v] = next_cost
        heapq.heappush(q, (next_cost, v))
# print(dist)
if dist[T] == INF:
    print(-1)
else:
    print(dist[T])
