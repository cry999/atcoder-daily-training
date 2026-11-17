# >>> atcoder-stat >>>
# started_at  = 2026-11-07T07:12:24+09:00
# solved_at   = 2026-11-07T07:15:20+09:00
# duration_ms = 176549
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import math

A, B, K = map(int, input().split())

print(math.ceil(math.log(B, K) - math.log(A, K)))
