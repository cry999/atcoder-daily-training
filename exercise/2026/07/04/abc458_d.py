# >>> atcoder-stat >>>
# started_at  = 2026-07-04T20:23:13+09:00
# solved_at   = 2026-07-04T20:29:41+09:00
# duration_ms = 388380
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from sortedcontainers import SortedList

X = int(input())
Q = int(input())

c = SortedList([X])
for _ in range(Q):
    a, b = map(int, input().split())
    c.add(a)
    c.add(b)
    print(c[len(c) // 2])
