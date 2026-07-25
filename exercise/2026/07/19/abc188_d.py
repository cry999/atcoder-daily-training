# >>> atcoder-stat >>>
# started_at  = 2026-07-19T16:27:25+09:00
# solved_at   = 2026-07-19T16:34:13+09:00
# duration_ms = 408321
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from collections import defaultdict

N, C = map(int, input().split())

events: defaultdict[int, int] = defaultdict(int)

for _ in range(N):
    a, b, c = map(int, input().split())
    events[a] += c
    events[b + 1] -= c

total_cost = 0
cur_cost = 0
cur_day = 0
for day in sorted(events):
    print(f"[DEBUG] {day=}, {events[day]=}: {cur_cost=}, {cur_day=}")
    total_cost += min(cur_cost, C) * (day - cur_day)

    cur_cost += events[day]
    cur_day = day

    print(f"[DEBUG] -> {total_cost=}")

assert cur_cost == 0

print(total_cost)
