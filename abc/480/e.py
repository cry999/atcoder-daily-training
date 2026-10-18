import math

N = int(input())


def ok(a: int, d: int, k: int):
    """a: 初項, d: 公差, k: 項数"""
    p = 1
    for i in range(k):
        p *= a + i * d
        if p > N:
            return False
    return True


ans = 0
k = 3
fact = 3 * 2 * 1
while fact <= N:
    a = 1
    while ok(a, 1, k):
        lo, hi = 1, math.isqrt(N // 2) + 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if ok(a, mid, k):
                lo = mid
            else:
                hi = mid

        ans += lo
        a += 1
    k += 1
    fact *= k

print(ans)
