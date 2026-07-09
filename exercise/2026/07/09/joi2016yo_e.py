import heapq

N, M, K, S = map(int, input().split())
P, Q = map(int, input().split())

g = [[] for _ in range(N + 1)]

cannot_visit = [False] * (N + 1)
q = []
for _ in range(K):
    c = int(input())
    cannot_visit[c] = True
    heapq.heappush(q, (0, c))

for _ in range(M):
    u, v = map(int, input().split())
    g[u].append(v)
    g[v].append(u)

# まずは危険なまちをダイクストラ法で求める
is_danger = [False] * (N + 1)
while q:
    s, u = heapq.heappop(q)
    if s >= S:
        continue
    for v in g[u]:
        if is_danger[v] or cannot_visit[v]:
            continue
        is_danger[v] = True
        heapq.heappush(q, (s + 1, v))

costs = [-1] * (N + 1)
costs[1] = 0
q = [(0, 1)]
while q:
    cost, cur = heapq.heappop(q)
    for v in g[cur]:
        if cannot_visit[v]:
            continue
        if v == N:
            new_cost = cost
        elif is_danger[v]:
            new_cost = cost + Q
        else:
            new_cost = cost + P
        if 0 <= costs[v] <= new_cost:
            continue
        costs[v] = new_cost
        heapq.heappush(q, (new_cost, v))

print(costs[N])
