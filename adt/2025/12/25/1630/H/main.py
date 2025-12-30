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


primes, factors = eratosthenes(10**6)
numbers_400 = []
for i, num_factor in enumerate(factors):
    if num_factor == 2:
        numbers_400.append(i**2)

Q = int(input())
for _ in range(Q):
    n = int(input())
    lo, hi = 0, len(numbers_400)
    while hi - lo > 1:
        mi = (lo + hi) // 2
        if numbers_400[mi] > n:
            hi = mi
        else:
            lo = mi
    print(numbers_400[lo])
