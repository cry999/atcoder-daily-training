# >>> atcoder-stat >>>
# started_at  = 2026-07-19T16:51:13+09:00
# solved_at   = 2026-07-19T17:29:04+09:00
# duration_ms = 2271024
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
import sys
from sortedcontainers import SortedList

input = sys.stdin.readline

N, Q = map(int, input().split())
events = []
for _ in range(N):
    s, t, x = map(int, input().split())
    events.append((s - x, x))
    events.append((t - x, -x))
events.sort()
print(f"[DEBUG] {events=}")
active = SortedList()
i = 0
for _ in range(Q):
    d = int(input())
    print(f"[DEBUG] {d=} @{active=}")

    while i < len(events) and events[i][0] <= d:
        time, x = events[i]
        print(f"[DEBUG]   {time=} {x=}")
        if x > 0:
            active.add(x)
        else:
            active.remove(-x)
        i += 1

    if active:
        print(active[0])
    else:
        print(-1)
