# >>> atcoder-stat >>>
# started_at  = 2026-07-22T18:41:49+09:00
# solved_at   = 2026-07-22T18:43:58+09:00
# duration_ms = 129471
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import functools
import sys

sys.setrecursionlimit(10**7)

N = int(input())


@functools.cache
def f(x: int):
    if x == 0:
        return 1
    return f(x // 2) + f(x // 3)


print(f(N))
