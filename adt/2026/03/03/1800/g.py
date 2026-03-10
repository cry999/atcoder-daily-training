N, A, B = map(int, input().split())


def gcd(a: int, b: int) -> int:
    if a < b:
        a, b = b, a

    while b:
        a, b = b, a % b

    return a


def lcm(a: int, b: int) -> int:
    return a * b // gcd(a, b)


na = N // A
nb = N // B
nab = N // lcm(A, B)

s = N * (N + 1) // 2
s -= A * na * (na + 1) // 2
s -= B * nb * (nb + 1) // 2
s += lcm(A, B) * nab * (nab + 1) // 2

print(s)
