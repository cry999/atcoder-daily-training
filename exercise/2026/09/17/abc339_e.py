# >>> atcoder-stat >>>
# started_at  = 2026-09-17T20:40:53+09:00
# <<< atcoder-stat <<<
from atcoder.lazysegtree import LazySegTree


def op(value1: int, value2: int):
    return max(value1, value2)


def mapping(f: int | None, value: int):
    return value if f is id_ else f


# 上のブロックの作用素を下のブロックの作用素に伝播
def composition(f: int | None, g: int):
    return g if f is id_ else f


# 値の単位元
e = -float("inf")

# 作用素の単位元
id_ = None
MAX = 5 * 10**5

lst = LazySegTree(op, e, mapping, composition, id_, [0] * (MAX + 1))

N, D = map(int, input().split())
(*A,) = map(int, input().split())

ans = 0
for a in A:
    l = lst.prod(max(0, a - D), min(MAX, a + D) + 1)
    ans = max(ans, l + 1)
    lst.set(a, l + 1)
print(ans)
