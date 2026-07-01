# >>> atcoder-stat >>>
# started_at  = 2026-07-01T13:53:05+09:00
# solved_at   = 2026-07-01T14:26:58+09:00
# duration_ms = 2033511
# target_ms   = 900000
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 1
# complexity  = 3
# impl        = 1
# verify      = 1
# <<< atcoder-stat <<<
from math import isqrt

Q = int(input())
for _ in range(Q):
    a, b = map(int, input().split())
    if a > b:
        a, b = b, a

    n = a * b
    k = isqrt(n - 1)
    ans = 2 * k
    if k * (k + 1) >= n:
        ans -= 1
    if a <= k:
        ans -= 1
    print(ans)
