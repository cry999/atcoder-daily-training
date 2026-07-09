import heapq
import sys

input = sys.stdin.readline

N, K = map(int, input().split())
g = [[] for _ in range(N + 1)]

for _ in range(K):
    q, *args = map(int, input().split())

    if q == 0:
        s, t = args
        dist = [-1] * (N + 1)
        queue = [(0, s)]
        while queue:
            d, u = heapq.heappop(queue)
            if u == t:
                print(d)
                break
            for v, dd in g[u]:
                if 0 <= dist[v] <= d + dd:
                    continue
                dist[v] = d + dd
                heapq.heappush(queue, (dist[v], v))
        else:
            print(-1)
    else:
        u, v, w = args
        g[u].append((v, w))
        g[v].append((u, w))
