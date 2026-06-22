import sys

input = sys.stdin.readline

N, Q = map(int, input().split())
g = [[] for _ in range(N)]

for _ in range(N - 1):
    a, b = map(int, input().split())
    a -= 1
    b -= 1
    g[a].append(b)
    g[b].append(a)

ans = [0] * N
for _ in range(Q):
    p, x = map(int, input().split())
    p -= 1
    ans[p] += x

q = [(0, -1)]
for u, p in q:
    for v in g[u]:
        if v == p:
            continue
        ans[v] += ans[u]
        q.append((v, u))

print(*ans)
