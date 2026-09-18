# >>> atcoder-stat >>>
# started_at  = 2026-09-17T18:11:08+09:00
# solved_at   = 2026-09-17T18:34:59+09:00
# duration_ms = 1431308
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import sys
from sortedcontainers import SortedList

input = sys.stdin.readline


N = int(input())
A = [int(input()) for _ in range(N)]

finals = SortedList()
for a in A:
    i = finals.bisect_left(a)
    print(f"[DEBUG] {a=} {i=} {finals=}")
    if i > 0 and finals[i - 1] < a:
        finals.pop(i - 1)
        finals.add(a)
    else:
        finals.add(a)
print(len(finals))
