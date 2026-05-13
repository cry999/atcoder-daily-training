import functools
from bisect import bisect_left

N = int(input())


@functools.cache
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


primes, _ = eratosthenes(10**6)

ans = 0
for q in primes[1:]:
    q3 = q**3
    if q3 > N:
        break
    pmax = min(N // q3, q)
    i = bisect_left(primes, pmax)
    p = primes[i]
    if p == q:
        i -= 1
        p = primes[i]
    while i > 0 and primes[i] * q3 > N:
        i -= 1
    if primes[i] * q3 > N or p >= q:
        continue

    ans += i + 1
    # print(p, q, p * q3, i + 1)
print(ans)
