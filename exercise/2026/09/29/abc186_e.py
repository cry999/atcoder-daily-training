# >>> atcoder-stat >>>
# started_at  = 2026-09-29T14:48:49+09:00
# solved_at   = 2026-09-29T14:57:19+09:00
# duration_ms = 510209
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from math import gcd

T = int(input())

for _ in range(T):
    N, S, K = map(int, input().split())

    d = gcd(K, N)

    if S % d != 0:
        print(-1)
    else:
        print(-(S // d * pow(K // d, -1, N // d)) % (N // d))
