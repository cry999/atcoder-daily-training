# >>> atcoder-stat >>>
# started_at  = 2026-11-17T08:43:46+09:00
# solved_at   = 2026-11-17T09:43:16+09:00
# duration_ms = 3570292
# ac          = true
# editorial   = true
# knowledge   = 2
# translation = 1
# complexity  = 2
# impl        = 2
# verify      = 2
# <<< atcoder-stat <<<
from atcoder.segtree import SegTree

N, Q = map(int, input().split())
(*A,) = map(int, input().split())

E = (0, 0)
V2 = (2, 0)


def op(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int]:
    if a[0] == 0 or b[0] == 2:
        return b
    if b[0] == 0 or a[0] == 2:
        return a
    assert a[0] == b[0] == 1
    return a if a[1] == b[1] else V2


seg = SegTree(op, E, [(1, a) if a >= 0 else E for a in A])

for _ in range(Q):
    q, *args = map(int, input().split())
    if q == 1:
        i, x = args
        seg.set(i - 1, (1, x) if x >= 0 else E)
    else:
        l, r = args
        n, _ = seg.prod(l - 1, r)  # pyright: ignore[reportAny]
        if n < 2:
            print("Yes")
        else:
            print("No")
