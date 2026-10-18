from atcoder.lazysegtree import LazySegTree

INF = 10**18


def mapping(f: int, x: int):
    return x + f if x != INF else INF


def composition(f: int, g: int):
    return f + g


N = int(input())
(*A,) = map(int, input().split())

dp = [INF] * (N + 1)
dp[0] = 0
seg = LazySegTree(min, INF, mapping, composition, 0, [INF] * N)

mins, maxs = [], []
for i, a in enumerate(A):
    seg.set(i, dp[i])

    j = i
    while maxs and maxs[-1][0] <= a:
        v, left = maxs.pop()
        seg.apply(left, j, a - v)
        j = left
    maxs.append((a, j))

    j = i
    while mins and mins[-1][0] >= a:
        v, left = mins.pop()
        seg.apply(left, j, v - a)
        j = left
    mins.append((a, j))

    dp[i + 1] = seg.prod(0, i)

print(dp[N])
