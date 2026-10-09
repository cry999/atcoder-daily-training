# >>> atcoder-stat >>>
# started_at  = 2026-10-06T10:26:37+09:00
# solved_at   = 2026-10-06T10:28:06+09:00
# duration_ms = 89568
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from functools import reduce

N = int(input())
(*A,) = map(int, input().split())

a = reduce(lambda x, y: x ^ y, A)
if a == 0:
    print("Bob")
else:
    print("Alice")
