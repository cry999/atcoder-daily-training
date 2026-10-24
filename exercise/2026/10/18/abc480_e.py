# >>> atcoder-stat >>>
# started_at  = 2026-10-18T14:36:59+09:00
# <<< atcoder-stat <<<
import math

N = int(input())


def ok(a: int, d: int, n: int):
    p = N
    for i in range(n):
        p //= a + i * d
        if p == 0:
            return False
    return p > 0


ans = 0
n = 3
fact = 3 * 2 * 1
while fact <= N:
    a = 1
    while ok(a, 1, n):
        if fact > N:
            break
        lo, hi = 0, math.isqrt(N // 2) + 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if ok(a, mid, n):
                lo = mid
            else:
                hi = mid
        ans += lo
        a += 1

    n += 1
    fact *= n
print(ans)
