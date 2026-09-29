import sys
from atcoder.lazysegtree import LazySegTree

input = sys.stdin.readline


def op(x: tuple[int], y: tuple[int]):
    return (x[0] + y[0], x[1] + y[1])


def mapping(f: int, x: int):
    return (x[0] + f * x[1], x[1])


def composition(func_upper: int, func_lower: int):
    return func_upper + func_lower


E = (0, 0)
ID = 0

N, M, Q = map(int, input().split())
rows = []
for _ in range(N):
    rows.append(tuple(map(int, input().split())))

# 累積和
events = []
for i in range(Q):
    a, b, c, d = map(int, input().split())
    events.append((b, 1, c, d, i))
    events.append((a - 1, -1, c, d, i))

events.sort()

# TODO (初期リストlst)
seg = LazySegTree(op, E, mapping, composition, ID, [(0, 1)] * (M + 2))
ans = [0] * Q
cur = 0
for r, sig, c, d, i in events:
    while cur < r:
        seg.apply(rows[cur][0], rows[cur][1] + 1, 1)
        cur += 1

    ans[i] += sig * seg.prod(c, d + 1)[0]

for i in range(Q):
    print(ans[i])
