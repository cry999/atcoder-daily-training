# >>> atcoder-stat >>>
# started_at  = 2026-07-04T11:53:02+09:00
# solved_at   = 2026-07-04T12:02:45+09:00
# duration_ms = 583547
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<

N, D = map(int, input().split())

events = []
for _ in range(N):
    entry, out = map(int, input().split())
    if out - entry < D:
        continue
    events.append((entry, +1))
    events.append((out - D + 1, -1))

events.sort()

in_house = 0  # 館にいる人数
event_cur = 0
ans = 0
for t in range(1, 10**6 + 1):
    while event_cur < len(events) and events[event_cur][0] == t:
        _, d = events[event_cur]
        in_house += d
        event_cur += 1

    ans += in_house * (in_house - 1) // 2
print(ans)
