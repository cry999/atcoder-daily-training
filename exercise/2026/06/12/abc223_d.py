from heapq import heappush, heappop

N, M = map(int, input().split())


g = [[] for _ in range(N + 1)]
dim = [0] * (N + 1)
for _ in range(M):
    a, b = map(int, input().split())
    # a -> b: トポロジカルソートする
    g[a].append(b)
    dim[b] += 1


ans = []


q = []
for j in range(1, N + 1):
    if dim[j] == 0:
        heappush(q, j)

node_num = 0
while q:
    u = heappop(q)
    node_num += 1
    ans.append(u)

    for v in g[u]:
        dim[v] -= 1
        if dim[v] == 0:
            heappush(q, v)

if node_num != N:
    # Kahn's algorithm
    ans = [-1]

print(*ans)
