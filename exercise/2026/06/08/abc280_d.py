N = int(input())


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


primes, _ = eratosthenes(10**6 + 1)

ans = -1
n = N
for p in primes:
    pn = 0
    while n % p == 0:
        n //= p
        pn += 1

    if pn == 0:
        continue

    lo, hi = 0, N // p
    while hi - lo > 1:
        mi = (lo + hi) // 2
        X = p * mi

        k = 0
        while X > 1:
            X //= p
            k += X

        if k < pn:
            lo = mi
        else:
            hi = mi

    # print(p, pn, p * lo, p * hi)
    ans = max(ans, hi * p)

ans = max(ans, n)
print(ans)
