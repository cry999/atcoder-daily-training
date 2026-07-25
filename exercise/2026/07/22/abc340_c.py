# >>> atcoder-stat >>>
# started_at  = 2026-07-22T17:04:15+09:00
# solved_at   = 2026-07-22T17:11:37+09:00
# duration_ms = 442643
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import sys
import functools

sys.setrecursionlimit(10**7)


@functools.cache
def dfs(n: int):
    if n == 1:
        return 0
    return dfs(n // 2) + dfs(n - n // 2) + n


print(dfs(int(input())))
