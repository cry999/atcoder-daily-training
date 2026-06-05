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


primes, _ = eratosthenes(2 * 10**6)
ans = 0
for i, p1 in enumerate(primes):
    if p1**8 <= N:
        ans += 1

    sq_p1 = p1**2
    lo, hi = i, len(primes)
    while hi - lo > 1:
        mi = (lo + hi) // 2
        p2 = primes[mi]

        if sq_p1 * p2**2 <= N:
            lo = mi
        else:
            hi = mi

    ans += lo - i

print(ans)
