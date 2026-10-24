# >>> atcoder-stat >>>
# started_at  = 2026-10-24T09:43:41+09:00
# solved_at   = 2026-10-24T10:06:40+09:00
# duration_ms = 1379580
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 1
# verify      = 3
# <<< atcoder-stat <<<
import math


N = int(input())

# 考察
# 1. 公差 d と初項 a1 に対して、最大の要素数 n を二分探索で求める


def ok(a1: int, d: int, n: int) -> bool:
    m = N
    for i in range(n):
        m //= a1 + i * d
        if m == 0:
            return False
    return m > 0


ans = 0

a = 1
while a * (a + 1) * (a + 2) <= N:
    q = N // a
    ans += (math.isqrt(a * a + 8 * q) - 3 * a) // 4
    a += 1

n = 4
fact = 4 * 3 * 2 * 1

while fact <= N:
    a = 1
    upper = N

    while ok(a, 1, n):
        lo, hi = 1, upper + 1
        while hi - lo > 1:
            d = (lo + hi) // 2
            if ok(a, d, n):
                lo = d
            else:
                hi = d
        ans += lo
        upper = lo
        a += 1

    n += 1
    fact *= n

print(ans)
