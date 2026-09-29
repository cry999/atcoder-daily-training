# >>> atcoder-stat >>>
# started_at  = 2026-09-27T09:57:28+09:00
# solved_at   = 2026-09-27T10:03:56+09:00
# duration_ms = 388899
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from atcoder.lazysegtree import LazySegTree

N, M, Q = map(int, input().split())
rows = [tuple(map(int, input().split())) for _ in range(N)]

events = []
for i in range(Q):
    a, b, c, d = map(int, input().split())
    events.append((a - 1, -1, c, d, i))
    events.append((b, 1, c, d, i))
events.sort()


def op(x: tuple[int, int], y: tuple[int, int]):
    return (x[0] + y[0], x[1] + y[1])


E = (0, 0)


def mapping(f: int, x: tuple[int, int]):
    return (x[0] + f * x[1], x[1])


def composition(f: int, g: int):
    return f + g


ID = 0

lst = LazySegTree(op, E, mapping, composition, ID, [(0, 1)] * (M + 2))
cur = 0  # 現在見ている行
ans = [0] * Q
for r, sign, c, d, i in events:
    while cur < r:
        lst.apply(rows[cur][0], rows[cur][1] + 1, 1)
        cur += 1

    ans[i] += sign * lst.prod(c, d + 1)[0]

print("\n".join(map(str, ans)))
