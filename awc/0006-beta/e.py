from atcoder.lazysegtree import LazySegTree


def op(a: int, b: int) -> int:
    return a + b


e = 0


def mapping(lazy_upper: int, data_lower: int) -> int:
    return data_lower + lazy_upper


_id = 0


def composition(lazy_upper: int, lazy_lower: int) -> int:
    return lazy_upper + lazy_lower


N, Q = map(int, input().split())
(*S,) = map(int, input().split())

segtree = LazySegTree(op, e, mapping, composition, _id, S)

for _ in range(Q):
    q, *args = map(int, input().split())
    if q == 1:
        l, r = args
        print(segtree.prod(l - 1, r))
    else:  # q == 2
        x, v = args
        segtree.set(x - 1, v)
