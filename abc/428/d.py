from math import isqrt, log10


def f_sqrt(n: int) -> int:
    s = isqrt(n)
    while s*s > n:
        s -= 1
    while (s+1)*(s+1) <= n:
        s += 1
    return s


for _ in range(int(input())):
    c, d = map(int, input().split())
    count = 0
    for digit in range(1, int(log10(c+d))+2):
        lo_x = max(1, 10**(digit-1)-c)
        hi_x = min(d, (10**digit)-1-c)
        tmp = f_sqrt(c*(10**digit)+c+hi_x) - f_sqrt(c*(10**digit)+c+lo_x-1)
        # print(c, d, digit, tmp)
        if tmp > 0:
            count += tmp
    print(count)
