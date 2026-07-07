N = int(input())
g = [[] for _ in range(N + 1)]
for _ in range(N):
    u, _, *v = map(int, input().split())
    g[u].extend(v)

d = [-1] * (N + 1)
d[1] = 0
q = [1]
for u in q:
    for v in g[u]:
        if d[v] != -1:
            continue
        d[v] = d[u] + 1
        q.append(v)

for u in range(1, N + 1):
    print(u, d[u])
