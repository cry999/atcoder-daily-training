import heapq


N, M = map(int, input().split())

nodes = [[] for _ in range(N+1)]
for _ in range(M):
    A, B, C = map(int, input().split())
    nodes[A].append((B, C))
    nodes[B].append((A, C))

dist = [(float('inf'), None)] * (N+1)  # (cost, prev)
queue = [(0, 1)]  # (cost, node)
dist[1] = (0, None)

while queue:
    d, v = heapq.heappop(queue)
    if dist[v][0] < d:
        continue

    for nv, c in nodes[v]:
        nd = d + c
        if dist[nv][0] <= nd:
            continue
        dist[nv] = (nd, v)
        heapq.heappush(queue, (nd, nv))

ans = [N]
while True:
    v = ans[-1]
    _, nv = dist[v]
    if nv is None:
        break
    ans.append(nv)

print(*ans[::-1])
