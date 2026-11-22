# >>> atcoder-stat >>>
# started_at  = 2026-11-19T17:15:38+09:00
# solved_at   = 2026-11-19T17:27:09+09:00
# duration_ms = 691442
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from sortedcontainers import SortedList

N, L, R = map(int, input().split())
(*A,) = map(int, input().split())

prefix = [0] * (N + 1)
for i in range(N):
    prefix[i + 1] = prefix[i] + A[i]

prev = SortedList()
ans = 0
for p in prefix:
    l = prev.bisect_left(p - R)
    r = prev.bisect_right(p - L)
    print(f"[DEBUG] {p=}, {l=}, {r=}: {prev=}")
    ans += r - l
    prev.add(p)
print(ans)
