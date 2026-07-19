# >>> atcoder-stat >>>
# started_at  = 2026-07-18T20:22:20+09:00
# <<< atcoder-stat <<<
from math import log

P = float(input())


def f(x: float):
    return x + P / (4 ** (x / 3))


def df(x: float):
    return 1 - 2 * P * log(2) / (3 * 4 ** (x / 3))


# log2 = log(2)
# x = max(0, 3 * (log(2 * P * log2) - log(3)) / (2 * log2))
#
# print(x + P / pow(4, x / 3))

lo, hi = 0, 1000
eps = 1e-10
while hi - lo > eps:
    mid = (hi + lo) / 2
    if df(mid) < 0:
        lo = mid
    else:
        hi = mid
print(f(lo))
