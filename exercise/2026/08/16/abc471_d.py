# >>> atcoder-stat >>>
# started_at  = 2026-08-16T01:38:19+09:00
# solved_at   = 2026-08-16T01:41:18+09:00
# duration_ms = 179167
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
# from sortedcontainers import SortedList
import heapq
import sys

input = sys.stdin.readline

Q, V = map(int, input().split())

# q = SortedList()
q = []
for _ in range(Q):
    query, *args = map(int, input().split())

    if query == 1:
        t0, w0 = args
        # q.add(w0 - t0)
        heapq.heappush(q, -(w0 - t0))
    else:
        t = args[0]
        if q:
            # u0 = q.pop()
            u0 = heapq.heappop(q)
            print(min(V, -u0 + t))
        else:
            print(-1)
