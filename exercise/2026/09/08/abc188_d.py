# >>> atcoder-stat >>>
# started_at  = 2026-09-08T15:09:52+09:00
# solved_at   = 2026-09-08T15:17:41+09:00
# duration_ms = 469645
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, C = map(int, input().split())

events = []
for _ in range(N):
    s, t, price = map(int, input().split())
    events.append((s, price))
    events.append((t + 1, -price))
events.sort()

current_price = 0
previous_time = 0

ans = 0

i = 0
while i < len(events):
    time, p = events[i]
    print(f"[DEBUG] {previous_time}-{time}: +{current_price}")
    ans += min(current_price, C) * (time - previous_time)

    current_price += p
    previous_time = time

    if i + 1 < len(events) and events[i + 1][0] == time:
        _, p = events[i + 1]
        current_price += p
        i += 1
    i += 1
print(ans)
