# >>> atcoder-stat >>>
# started_at  = 2026-07-07T06:28:27+09:00
# solved_at   = 2026-07-07T06:44:36+09:00
# duration_ms = 969950
# ac          = true
# editorial   = false
# knowledge   = 2
# translation = 2
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from math import log

P = float(input())


def f(x: float):
    return x + P / (4 ** (x / 3))


def df(x: float):
    return 1 - P * log(4) / (3 * 4 ** (x / 3))


lo, hi = 0, 100
eps = 1e-9
while hi - lo > eps:
    # c1 = (2 * lo + hi) / 3  # lo 寄り
    # c2 = (lo + 2 * hi) / 3  # hi 寄り
    #
    # if f(c1) < f(c2):
    #     hi = c2
    # else:
    #     lo = c1
    mid = (lo + hi) / 2
    if df(mid) < 0:
        lo = mid
    else:
        hi = mid

print(f(lo))
