N = int(input())


def digit(x: int) -> int:
    d = 0
    while x:
        d += 1
        x //= 10
    return d


def sum_digit(x: int) -> int:
    d = 0
    while x:
        d += x % 10
        x //= 10
    return d


if N < 10**6:
    for n in range(N, 2*N):
        d = sum_digit(n)
        if d == 0 or n % d:
            continue

        d = sum_digit(n+1)
        if d == 0 or (n+1) % d:
            continue

        print(n)
        break
    else:
        print(-1)
else:
    d = digit(N)
    B = 10**(d-2)
    x = N // B
    if x <= 16:
        print(17*B)
    elif x <= 25:
        print(26*B)
    elif x <= 34:
        print(35*B)
    elif x <= 61:
        print(62*B)
    else:
        print(107*B)
