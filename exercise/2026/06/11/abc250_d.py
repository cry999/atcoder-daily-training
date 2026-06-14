N = int(input())


def eratosthenes(n: int):
    is_not_prime = [0] * (n + 1)
    primes = []

    for p in range(2, n + 1):
        if is_not_prime[p]:
            continue
        primes.append(p)
        for k in range(p, n + 1, p):
            is_not_prime[k] += 1
    return primes, is_not_prime


primes, _ = eratosthenes(10**6)
M = len(primes)
# print(M)
ans = 0
for i in range(M):
    p = primes[i]

    lo, hi = i, M
    while hi - lo > 1:
        mi = (lo + hi) // 2
        q = primes[mi]

        if p * q**3 <= N:
            lo = mi
        else:
            hi = mi

    if lo == i:
        break
    ans += lo - i
print(ans)
