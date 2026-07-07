N = int(input())
g = [[] for _ in range(N + 1)]
for _ in range(N):
    u, _, *v = map(int, input().split())
    v.sort()
    g[u].extend(v)

d = [-1] * (N + 1)
f = [-1] * (N + 1)


def dfs(u: int, time: int = 1):
    d[u] = time
    for v in g[u]:
        if d[v] != -1:
            continue
        time = dfs(v, time + 1)
    f[u] = time + 1
    return f[u]


time = 1
for u in range(1, N + 1):
    if d[u] != -1:
        continue
    time = dfs(u, time) + 1

for u in range(1, N + 1):
    print(u, d[u], f[u])
