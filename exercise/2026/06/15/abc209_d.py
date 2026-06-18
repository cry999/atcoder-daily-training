import sys

input = sys.stdin.readline
print = sys.stdout.write


N, Q = map(int, input().split())
g = [[] for _ in range(N + 1)]
for _ in range(N - 1):
    a, b = map(int, input().split())
    g[a].append(b)
    g[b].append(a)

q = [(1, -1)]
depth = [0] * (N + 1)

for u, p in q:
    for v in g[u]:
        if v == p:
            continue
        depth[v] = depth[u] + 1
        q.append((v, u))

ans = [None] * Q
for i in range(Q):
    c, d = map(int, input().split())
    if (depth[c] + depth[d]) % 2:
        ans[i] = "Road"
    else:
        ans[i] = "Town"

print("\n".join(ans))
