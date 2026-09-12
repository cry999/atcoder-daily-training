# >>> atcoder-stat >>>
# started_at  = 2026-09-11T14:29:38+09:00
# solved_at   = 2026-09-11T14:50:01+09:00
# duration_ms = 1223997
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 1
# complexity  = 3
# impl        = 1
# verify      = 3
# <<< atcoder-stat <<<
from heapq import heappush, heappop, heapify
import sys

input = sys.stdin.readline


INF = float("inf")

# 1. 総和から増分に視点を切り替える
# 2. 増分が減少し続けることから、商品として区別しても最適なナップサックができることに気づく。

N, W = map(int, input().split())

# heaps[w] := 重さが w の時の嬉しさのあたい
heaps = [[] for _ in range(W + 1)]

for _ in range(N):
    w, v = map(int, input().split())
    heaps[w].append(-(v - 1))

dp = [-INF] * (W + 1)
dp[0] = 0
for w in range(1, W + 1):
    h = heaps[w]
    if not h:
        continue
    heapify(h)

    for _ in range(W // w):
        gain = -heappop(h)
        if gain <= 0:
            break

        for s in range(W, w - 1, -1):
            dp[s] = max(dp[s], dp[s - w] + gain)

        heappush(h, -(gain - 2))

print(max(dp))
