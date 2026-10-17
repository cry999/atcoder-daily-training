# >>> atcoder-stat >>>
# started_at  = 2026-10-10T11:40:19+09:00
# solved_at   = 2026-10-10T11:55:22+09:00
# duration_ms = 903045
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())
g = [[] for _ in range(N)]
for _ in range(N - 1):
    x, y = map(int, input().split())
    x -= 1
    y -= 1
    g[x].append(y)
    g[y].append(x)


M = 20

q = [0]
par = [[-1] * N for _ in range(M)]
dep = [0] * N
for u in q:
    for v in g[u]:
        if v == par[0][u]:
            continue
        par[0][v] = u
        dep[v] = dep[u] + 1
        q.append(v)

for k in range(M - 1):
    par[k + 1] = [par[k][par[k][u]] if par[k][u] >= 0 else -1 for u in range(N)]


def lca(u: int, v: int):
    if dep[u] > dep[v]:
        u, v = v, u

    for k in range(M):
        if ((dep[v] - dep[u]) >> k) & 1:
            v = par[k][v]

    if u == v:
        return u

    for k in range(M - 1, -1, -1):
        if par[k][u] != par[k][v]:
            u, v = par[k][u], par[k][v]

    return par[0][u]


Q = int(input())
for _ in range(Q):
    a, b = map(int, input().split())
    a -= 1
    b -= 1

    p = lca(a, b)
    ans = (dep[a] - dep[p]) + (dep[b] - dep[p]) + 1
    print(ans)
