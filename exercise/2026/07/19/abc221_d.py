# >>> atcoder-stat >>>
# started_at  = 2026-07-19T16:17:50+09:00
# solved_at   = 2026-07-19T16:25:38+09:00
# duration_ms = 468589
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
import sys

input = sys.stdin.readline

N = int(input())

events: defaultdict[int, int] = defaultdict(int)
for _ in range(N):
    a, b = map(int, input().split())
    events[a] += 1  # a 日目にログイン人数が 1 人増える
    events[a + b] -= 1  # a+b 日目にログイン人数が 1 人減る


# D[i] := i+1 人がログインしていた日数
D = [0] * N

cur_active_user = 0
cur_day = 0
for day in sorted(events):
    if cur_active_user > 0:
        D[cur_active_user - 1] += day - cur_day

    cur_active_user += events[day]
    cur_day = day

assert cur_active_user == 0

print(*D)
