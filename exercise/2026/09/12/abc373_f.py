# >>> atcoder-stat >>>
# started_at  = 2026-09-12T18:14:25+09:00
# solved_at   = 2026-09-12T18:25:45+09:00
# duration_ms = 680526
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from heapq import heappush
from math import inf
from heapq import heappop
from heapq import heapify
import sys

input = sys.stdin.readline


N, W = map(int, input().split())

# 同じ重さの荷物を差分で考える。
# 同じ種類の荷物について
# 1 つめは v - 1
# 2 つめは v - 3
# ...
# の価値と考えて個別の荷物に変換する。
# k+1 個目の同じ種類の荷物の価値は k 個目より低くなるので、
# k 個目より先に選ばれることはなく、個数の不整合は起きない。

values = [[] for _ in range(W + 1)]
for _ in range(N):
    w, v = map(int, input().split())
    values[w].append(-(v - 1))

dp = [-inf] * (W + 1)
dp[0] = 0
for w in range(W + 1):
    if not values[w]:
        continue

    value_queue = values[w].copy()
    heapify(value_queue)

    # 同じ重さの荷物は最大で W // w 個しか詰めない
    for _ in range(W // w):
        if not value_queue:
            break
        v = -heappop(value_queue)
        if v <= 0:
            continue

        for s in range(W, w - 1, -1):
            dp[s] = max(dp[s], dp[s - w] + v)

        # 同じ種類の次の価値を積んでおく
        if v - 2 > 0:
            heappush(value_queue, -(v - 2))

print(max(dp))
