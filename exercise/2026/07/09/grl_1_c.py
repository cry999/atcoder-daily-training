V, E = map(int, input().split())

INF = float("inf")
dist = [[INF] * V for _ in range(V)]
for _ in range(E):
    s, t, d = map(int, input().split())
    dist[s][t] = d

for i in range(V):
    dist[i][i] = 0

for k in range(V):
    for s in range(V):
        for t in range(V):
            dist[s][t] = min(dist[s][t], dist[s][k] + dist[k][t])

if any(dist[i][i] < 0 for i in range(V)):
    print("NEGATIVE CYCLE")
else:
    for r in dist:
        print(" ".join(str(x) if x != INF else "INF" for x in r))
