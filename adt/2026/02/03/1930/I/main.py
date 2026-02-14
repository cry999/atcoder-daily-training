from atcoder.lazysegtree import LazySegTree


N, M = map(int, input().split())
(*A,) = map(int, input().split())

MOD = 998244353


def op(x: int, y: int) -> int:
    return x + y


def mapping(f: tuple[int, int], x: int) -> int:
    a, b = f
    return (a * x + b) % MOD


def composition(f: tuple[int, int], g: tuple[int, int]) -> tuple[int, int]:
    a1, b1 = f
    a2, b2 = g
    return ((a1 * a2) % MOD, (a1 * b2 + b1) % MOD)


e = 0
id_ = (1, 0)

E = [a % MOD for a in A]
lazy_segtree = LazySegTree(op, e, mapping, composition, id_, E)

for _ in range(M):
    L, R, X = map(int, input().split())
    inv = pow(R - L + 1, MOD - 2, MOD)
    a = ((R - L) * inv) % MOD
    b = (X * inv) % MOD
    lazy_segtree.apply(L - 1, R, (a, b))
    # for i in range(L - 1, R):
    #     E[i] = (E[i] * (R - L) + X) * pow(R - L + 1, MOD - 2, MOD)
    #     E[i] %= MOD

# print(*E)
print(*[lazy_segtree.get(i) for i in range(N)])
