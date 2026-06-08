from bisect import bisect_left

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


primes, _ = eratosthenes(10**6)
M = len(primes)

ans = []

for i in range(M):
    a = primes[i]
    if a**5 >= N:
        break

    for j in range(i + 1, M):
        b = primes[j]
        if a**2 * b**3 >= N:
            break

        for k in range(j + 1, M):
            c = primes[k]
            if a**2 * b * c**2 > N:
                break

            ans.append(a**2 * b * c**2)

ans.sort()
i = bisect_left(ans, N)
if i < len(ans) and ans[i] == N:
    i += 1
print(i)
