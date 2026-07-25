# >>> atcoder-stat >>>
# started_at  = 2026-07-20T10:21:19+09:00
# <<< atcoder-stat <<<
from sortedcontainers import SortedList

N, Q = map(int, input().split())
events = []
for _ in range(N):
    s, t, x = map(int, input().split())
    events.append((s - x, x))
    events.append((t - x, -x))
events.sort()

active = SortedList()
i = 0
for _ in range(Q):
    d = int(input())
    while i < len(events) and events[i][0] <= d:
        _, x = events[i]
        if x > 0:
            active.add(x)
        else:
            active.remove(-x)
        i += 1

    if active:
        print(active[0])
    else:
        print(-1)
