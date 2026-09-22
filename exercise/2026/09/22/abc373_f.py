# >>> atcoder-stat >>>
# started_at  = 2026-09-22T16:43:43+09:00
# solved_at   = 2026-09-22T16:52:21+09:00
# duration_ms = 518948
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import heapq
import sys

input = sys.stdin.readline
N, W = map(int, input().split())

values_by_weight = [[] for _ in range(W + 1)]
for _ in range(N):
    w, v = map(int, input().split())
    values_by_weight[w].append(-(v - 1))

# dp[w] := 重さがちょうど w の時の最大価値
dp = [0] * (W + 1)
for w in range(W + 1):
    weights = values_by_weight[w]
    if not weights:
        continue

    heapq.heapify(weights)
    for _ in range(W // w):
        if not weights:
            break

        v = -heapq.heappop(weights)
        for x in range(W - w, -1, -1):
            dp[x + w] = max(dp[x + w], dp[x] + v)

        heapq.heappush(weights, -(v - 2))

print(max(dp))
