# >>> atcoder-stat >>>
# started_at  = 2026-09-17T17:03:59+09:00
# solved_at   = 2026-09-17T17:22:22+09:00
# duration_ms = 1103215
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 1
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from heapq import heappush, heapify, heappop

N, L = map(int, input().split())
(*A,) = map(int, input().split())

r = L - sum(A)
if r:
    A.append(r)

heapify(A)

ans = 0
while len(A) > 1:
    nxt = heappop(A) + heappop(A)

    ans += nxt
    heappush(A, nxt)

print(ans)
