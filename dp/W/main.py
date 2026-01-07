from atcoder.lazysegtree import LazySegTree


N, M = map(int, input().split())
ranges = [[] for _ in range(N + 2)]
for _ in range(M):
    l, r, a = map(int, input().split())
    ranges[r].append((l, a))


# dp = LazySegmentTree(N + 1)
dp = LazySegTree(
    lambda x, y: max(x, y),  # op
    -float("inf"),  # e
    lambda f, x: x + f,  # mapping
    lambda f, g: f + g,  # composition
    0,  # id
    [0] + [-float("inf")] * N,
)

for r in range(1, N + 1):
    base = dp.prod(0, r)
    dp.set(r, base)

    for l, a in ranges[r]:
        dp.apply(l, r + 1, a)

print(dp.all_prod())
