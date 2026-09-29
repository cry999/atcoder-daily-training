import heapq

N, Q = map(int, input().split())
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())

prefix = [0] * (N + 1)
for i in range(N):
    prefix[i + 1] = prefix[i] + A[i]
total = prefix[N]

dist = B.copy()
q = [(dist[i], i) for i in range(N)]
heapq.heapify(q)

while q:
    c, u = heapq.heappop(q)
    if c != dist[u]:
        continue

    for v, w in [
        ((u + 1) % N, A[u]),
        ((u - 1) % N, A[(u - 1) % N]),
    ]:
        nc = c + w
        if nc < dist[v]:
            dist[v] = nc
            heapq.heappush(q, (nc, v))

for _ in range(Q):
    s, t = map(int, input().split())
    s, t = s - 1, t - 1

    if s == t:
        print(0)
        continue
    if s == N:
        print(dist[t])
        continue
    if t == N:
        print(dist[s])
        continue

    ans = min(
        abs(prefix[t] - prefix[s]),
        total - abs(prefix[t] - prefix[s]),
        dist[s] + dist[t],
    )
    print(ans)
