from atcoder.lazysegtree import LazySegTree

N, Q = map(int, input().split())
(*A,) = map(int, input().split())


def op(e1, e2):
    return e1 + e2


def mapping(func, e):
    return func + e


def composition(f, g):
    return f + g


e = 0
id_ = 0


t = LazySegTree(op, e, mapping, composition, id_, A)


for _ in range(Q):
    q, *args = map(int, input().split())
    if q == 1:
        x = args[0]

        a0, a1 = A[x - 1], A[x]
        A[x - 1], A[x] = a1, a0
        t.apply(x - 1, x, a1 - a0)
        t.apply(x, x + 1, a0 - a1)

    else:  # q == 2
        l, r = args
        print(t.prod(l - 1, r))
