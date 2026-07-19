# >>> atcoder-stat >>>
# started_at  = 2026-07-18T20:47:16+09:00
# solved_at   = 2026-07-18T20:52:41+09:00
# duration_ms = 325369
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from sortedcontainers import SortedList

N = int(input())
A = [int(input()) for _ in range(N)]

s = SortedList([-1])

for a in A:
    i = s.bisect_left(a) - 1
    if i < 0:
        s.add(a)
    else:
        s.pop(i)
        s.add(a)

print(len(s))
