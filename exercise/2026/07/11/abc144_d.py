# >>> atcoder-stat >>>
# started_at  = 2026-07-11T06:40:05+09:00
# solved_at   = 2026-07-11T06:54:19+09:00
# duration_ms = 854706
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from math import atan2, pi

a, b, x = map(int, input().split())

if a * a * b == 2 * x:
    theta = atan2(b, a)
elif a * a * b < 2 * x:
    y = 2 * x / (a * a) - b
    theta = atan2(b - y, a)
else:
    y = 2 * x / (a * b)
    theta = atan2(b, y)
print(theta * 360 / (2 * pi))
