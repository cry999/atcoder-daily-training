# >>> atcoder-stat >>>
# started_at  = 2026-09-04T06:51:58+09:00
# solved_at   = 2026-09-04T06:58:40+09:00
# duration_ms = 402508
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


# 累積和による解法 (O(N + max(T)))
N, W = map(int, input().split())
events = []
max_time = 0
for _ in range(N):
    s, t, p = map(int, input().split())
    events.append((s, p))
    events.append((t, -p))
    max_time = max(max_time, t)

cum = [0] * (max_time + 2)
for time, p in events:
    cum[time] += p

for t in range(max_time + 1):
    cum[t + 1] += cum[t]
    if cum[t] > W:
        print("No")
        break
else:
    print("Yes")


# # イベント処理による解法 (O(N log N))
# N, W = map(int, input().split())
# events = []
# for _ in range(N):
#     s, t, p = map(int, input().split())
#     events.append((s, p))
#     events.append((t, -p))
#
# events.sort()
# use = 0
# for _, p in events:
#     use += p
#     if use > W:
#         print("No")
#         break
# else:
#     print("Yes")
