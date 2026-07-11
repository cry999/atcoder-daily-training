# >>> atcoder-stat >>>
# started_at  = 2026-07-11T09:42:55+09:00
# solved_at   = 2026-07-11T10:26:01+09:00
# duration_ms = 2586178
# target_ms   = 900000
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 2
# verify      = 2
# <<< atcoder-stat <<<
from math import gcd

N, M = map(int, input().split())
(*A,) = map(int, input().split())

half_lcd = 1
for a in A:
    half_lcd *= a // 2 // gcd(half_lcd, a // 2)
    if half_lcd > M:
        half_lcd = M + 1
        break
for a in A:
    if half_lcd // (a // 2) % 2 == 0:
        print(0)
        exit()
m = M // half_lcd
print(m // 2 + m % 2)
