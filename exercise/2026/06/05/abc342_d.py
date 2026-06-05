import functools
from collections import defaultdict

N = int(input())
(*A,) = sorted(map(int, input().split()))


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


@functools.cache
def factors(n: int):
    res = 1
    while n > 1:
        for p in primes:
            if p > n:
                break
            k = 0
            while n % p == 0:
                k += 1
                n //= p

            if k % 2 > 0:
                res *= p
    return res


# squares[f] := 平方数でない f と平方数の組み合わせになっている A[i] の個数
# A[i] = f * (平方数)
squares = defaultdict(int)
for i in range(N):
    f = factors(A[i])
    squares[f] += 1

ans = 0
for i in range(N - 1):
    t = 0
    f = factors(A[i])
    squares[f] -= 1

    if A[i] == 0:
        # print(i, N - i - 1)
        ans += N - i - 1
        continue

    ans += squares[f]

print(ans)
