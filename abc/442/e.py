from math import atan2, gcd
from functools import cmp_to_key
from collections import defaultdict

monsters = defaultdict(int)
points = []

N, Q = map(int, input().split())
for _ in range(N):
    x, y = map(int, input().split())
    # (x, y) != (0, 0)
    if x == 0:
        x, y = 0, y // abs(y)
    elif y == 0:
        x, y = x // abs(x), 0
    else:  # x != 0 and y != 0
        d = gcd(abs(x), abs(y))
        x, y = x // d, y // d

    points.append((x, y))
    monsters[(x, y)] += 1


def half(p: tuple[int, int]):
    """0: 上半面, 1: 下半面"""
    x, y = p
    if y > 0:
        return 0
    if y == 0 and x > 0:
        return 0
    return 1


def cmp(a: tuple[int, int], b: tuple[int, int]):
    ax, ay = a
    bx, by = b
    ha, hb = half(a), half(b)
    if ha != hb:
        return -1 if ha < hb else 1

    c = ax * by - ay * bx
    if c == 0:
        return 0
    if c < 0:
        return -1
    return 1


# sorted_point_sets = sorted(set(points), key=lambda x: -atan2(x[1], x[0]))
sorted_point_sets = sorted(set(points), key=cmp_to_key(cmp))

cum = [0] * (len(sorted_point_sets) + 1)
index_in_sorted = {}
for i, p in enumerate(sorted_point_sets):
    cum[i + 1] = cum[i] + monsters[p]
    index_in_sorted[p] = i

for _ in range(Q):
    a, b = map(int, input().split())
    pa, pb = points[a - 1], points[b - 1]
    ia, ib = index_in_sorted[pa], index_in_sorted[pb]
    if ia <= ib:
        print(cum[ib + 1] - cum[ia])
    else:
        print(N - cum[ia] + cum[ib + 1])
