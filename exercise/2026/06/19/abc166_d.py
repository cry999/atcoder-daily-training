from math import isqrt

X = int(input())

for m in range(1, isqrt(X) + 1):
    if X % m != 0:
        continue

    # for m in [-mm, mm]:
    # A - B = m
    n = X // m

    # n - m^4 は 5 の倍数である必要がある。
    if (n - m**4) % 5 != 0:
        continue

    if n - m**4 == 0:
        print(m, 0)
        exit()

    z = abs(n - m**4) // 5
    if n - m**4 < 0:
        z = -z

    for x in range(1, isqrt(abs(z)) + 1):
        if z % x != 0:
            continue

        if z // x < 0:
            x = -x

        b = x
        if b**3 + 2 * m * b**2 + 2 * m**2 * b**1 + m**3 == z // b:
            print(m + b, b)
            exit()
    else:
        continue
