# >>> atcoder-stat >>>
# started_at  = 2026-11-19T17:08:51+09:00
# solved_at   = 2026-11-19T17:15:32+09:00
# duration_ms = 401775
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from collections import defaultdict

N = int(input())
(*A,) = map(int, input().split())

freq: defaultdict[int, int] = defaultdict(int)
ans = 1
prev = -1
for n, a in enumerate(A):
    if a != prev:
        ans += n - freq[a]
    freq[a] += 1
    prev = a
print(ans)
