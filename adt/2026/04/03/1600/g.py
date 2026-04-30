import functools

N, M = map(int, input().split())
(*A,) = map(int, input().split())


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


def factor(n: int, primes: list[int]) -> list[int]:
    factors = []
    for p in primes:
        if p > n:
            break
        if n % p != 0:
            continue

        factors.append(p)
        while n % p == 0:
            n //= p

    return factors


primes, _ = eratosthenes(M)

ans = [True] * (M + 1)
ans[0] = False

used = [False] * (10**5 + 1)
for a in A:
    if used[a]:
        continue
    factors = factor(a, primes)

    for f in factors:
        if used[f]:
            continue
        used[f] = True

        for d in range(f, M + 1, f):
            ans[d] = False

print(sum(ans))
for i in range(1, M + 1):
    if ans[i]:
        print(i)
