POW10 = [1] * 18
for i in range(1, 18):
    POW10[i] = POW10[i - 1] * 10


def f(s: str, digit: int, x: int) -> int:
    n = int(s)

    if n * 10 ** (digit - 1) > x:
        return 0

    d: int = 10 ** (digit - 1)
    ds: int = 10 ** len(s)
    lo, hi = 1, d * 10
    while hi - lo > 1:
        mi = (lo + hi) // 2

        m = mi - 1
        if s[0] == "0":
            m += d

        y = ((m - 1) - ((m - 1) % d)) * ds + n * d + ((m - 1) % d)

        if y <= x:
            lo = mi
        else:
            hi = mi

    return lo


def sum_f(s: str, x: int) -> int:
    ans = 0
    for k in range(16):
        ans += f(s, k, x)
    return ans


T = int(input())

for _ in range(T):
    s, raw_l, raw_r = input().split()
    l, r = int(raw_l), int(raw_r)

    ans = sum_f(s, r) - sum_f(s, l - 1)
    print(ans)
