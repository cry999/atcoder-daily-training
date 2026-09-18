# >>> atcoder-stat >>>
# started_at  = 2026-09-17T17:28:20+09:00
# solved_at   = 2026-09-17T18:10:30+09:00
# duration_ms = 2530779
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from bisect import bisect_left
import sys

input = sys.stdin.readline


N = int(input())
cards = [int(input()) for _ in range(N)]

INF = 10**18
length = [INF] * (N + 2)
length[0] = 0

for c in cards:
    i = bisect_left(length, c)
    length[i] = min(length[i], c)

max_length = -1
for x in length:
    if x == INF:
        break
    max_length += 1
print(N - max_length)
