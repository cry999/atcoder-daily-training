# >>> atcoder-stat >>>
# started_at  = 2026-10-09T11:04:08+09:00
# solved_at   = 2026-10-09T11:20:17+09:00
# duration_ms = 969618
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from atcoder.lazysegtree import LazySegTree

N, M = map(int, input().split())
(*A,) = map(int, input().split())  # N
(*B,) = map(int, input().split())  # M


def op(x: int, y: int):
    return min(x, y)


E = float("inf")


def mapping(f: int, x: int):
    return f + x


def composition(f: int, g: int):
    return f + g


ID = 0


seg = LazySegTree(op, E, mapping, composition, ID, A)

for b in B:
    x = seg.get(b)
    seg.set(b, 0)

    q, r = divmod(x, N)
    if q > 0:
        seg.apply(0, N, q)
    if r > 0:
        seg.apply(b + 1, min(b + 1 + r, N), 1)
        seg.apply(0, max(0, b + 1 + r - N), 1)

ans = [seg.get(i) for i in range(N)]
print(*ans)
