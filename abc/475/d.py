from math import isqrt


def sieve(n: int) -> list[int]:
    is_prime = bytearray(b"\x01") * (n + 1)
    is_prime[0:2] = b"\x00\x00"

    for p in range(2, isqrt(n) + 1):
        if is_prime[p]:
            start = p * p
            count = (n - start) // p + 1
            is_prime[start : n + 1 : p] = b"\x00" * count

    return [i for i in range(2, n + 1) if is_prime[i]]


(*S,) = reversed(input())
N = len(S)
M1 = 10**N
M2 = 10 ** (N - 1)


(*primes,) = filter(lambda x: M2 <= x < M1, sieve(9_999_999))

for p in primes:
    d = {}

    q = p
    used = [False] * 10
    ok = True
    for c in S:
        n = q % 10
        if c in d and d[c] != n:
            ok = False
            break
        if c not in d and used[n]:
            ok = False
            break
        d[c] = n
        used[n] = True
        q //= 10

    if ok:
        print(p)
        exit()
print(-1)
