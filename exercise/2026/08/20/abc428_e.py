# >>> atcoder-stat >>>
# started_at  = 2026-08-20T03:51:52+09:00
# solved_at   = 2026-08-20T04:01:21+09:00
# duration_ms = 569310
# ac          = true
# editorial   = false
# knowledge   = 2
# translation = 2
# complexity  = 3
# impl        = 1
# verify      = 3
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline

N = int(input())
g = [[] for _ in range(N)]

for _ in range(N - 1):
    u, v = map(int, input().split())
    u, v = u - 1, v - 1

    g[u].append(v)
    g[v].append(u)

# monoide の設定

E = (-1, -1)  # (最大距離, その時の頂点)


def merge(a: tuple[int], b: tuple[int]):
    if a[0] > b[0]:
        return a
    if a[0] < b[0]:
        return b
    return (a[0], max(a[1], b[1]))


def add_root(x: int, v: int):
    if x == E:
        return (0, v)
    return (x[0] + 1, x[1])


parent = [-1] * N
order = [0]

for u in order:
    for v in g[u]:
        if v == parent[u]:
            continue
        parent[v] = u
        order.append(v)

down = [E] * N
for u in reversed(order):
    x = E
    for v in g[u]:
        if v == parent[u]:
            continue
        x = merge(x, down[v])

    down[u] = add_root(x, u)

up = [E] * N
ans = [E] * N

for u in order:
    m = len(g[u])

    vals = [E] * m
    for i, v in enumerate(g[u]):
        if v == parent[u]:
            vals[i] = up[u]
        else:
            vals[i] = down[v]

    pre = [E] * (m + 1)
    suf = [E] * (m + 1)

    for i in range(m):
        pre[i + 1] = merge(pre[i], vals[i])

    for i in range(m - 1, -1, -1):
        suf[i] = merge(vals[i], suf[i + 1])

    _, ans[u] = add_root(pre[m], u)
    ans[u] += 1

    for i, v in enumerate(g[u]):
        if v == parent[u]:
            continue

        x = merge(pre[i], suf[i + 1])
        up[v] = add_root(x, u)

print(*ans, sep="\n")
