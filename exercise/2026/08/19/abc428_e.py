# >>> atcoder-stat >>>
# started_at  = 2026-08-19T16:37:31+09:00
# solved_at   = 2026-08-19T16:59:03+09:00
# duration_ms = 1292760
# ac          = true
# editorial   = false
# knowledge   = 3
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
    u -= 1
    v -= 1

    g[u].append(v)
    g[v].append(u)

# monoide の設定

E = (-1, -1)


def merge(a: tuple[int], b: tuple[int]) -> tuple[int]:
    if a[0] > b[0]:
        return a
    if a[0] < b[0]:
        return b
    return (a[0], max(a[1], b[1]))


def add_root(x: int, v: int) -> int:
    if x == E:
        return (0, v)
    d, u = x
    return (d + 1, u)


# BFS で親を求める (根つき木にする)

parent = [-1] * N
order = [0]

for u in order:
    for v in g[u]:
        if v == parent[u]:
            continue
        parent[v] = u
        order.append(v)

# 1. 下から上への DP
down = [E] * N
for u in reversed(order):
    x = E

    for v in g[u]:
        if v == parent[u]:
            continue
        x = merge(x, down[v])

    down[u] = add_root(x, u)

# 2. 上から下への DP
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

    prefix = [E] * (m + 1)
    suffix = [E] * (m + 1)

    for i in range(m):
        prefix[i + 1] = merge(prefix[i], vals[i])

    for i in range(m - 1, -1, -1):
        suffix[i] = merge(vals[i], suffix[i + 1])

    _, ans[u] = add_root(prefix[m], u)
    ans[u] += 1

    for i, v in enumerate(g[u]):
        if v == parent[u]:
            continue

        x = merge(prefix[i], suffix[i + 1])
        up[v] = add_root(x, u)

print(*ans, sep="\n")
