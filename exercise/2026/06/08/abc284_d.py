from math import isqrt


def eratosthenes(n: int) -> tuple[list[int], list[int]]:
    is_prime = [0] * (n + 1)
    primes = []
    for p in range(2, n + 1):
        if is_prime[p]:
            continue
        primes.append(p)
        for k in range(p, n + 1, p):
            is_prime[k] += 1

    return primes, is_prime


primes, _ = eratosthenes(3 * 10**6)

T = int(input())

for _ in range(T):
    N = int(input())
    p, q = -1, -1
    for prime in primes:
        if N % (prime**2) == 0:
            p = prime
            q = N // (p**2)
            break
        if N % prime == 0:
            q = prime
            p = isqrt(N // q)
            break
    print(p, q)
