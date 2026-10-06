# >>> atcoder-stat >>>
# started_at  = 2026-10-04T09:24:17+09:00
# solved_at   = 2026-10-04T09:33:52+09:00
# duration_ms = 575574
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline


N, Q = map(int, input().split())

events = []
for _ in range(Q):
    l, r, x = map(int, input().split())
    events.append((l - 1, x, +1))
    events.append((r, x, -1))

events.sort()

counter = [0] * (Q + 1)
covered = 0

ans = [0] * N
j = 0
for i in range(N):
    while j < len(events) and events[j][0] == i:
        _, x, d = events[j]

        if counter[x] == 0:
            covered += 1
        counter[x] += d
        if counter[x] == 0:
            covered -= 1

        j += 1

    ans[i] = covered

print(*ans)
