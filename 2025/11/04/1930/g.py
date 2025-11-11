from math import isqrt


N = int(input())

sqrt_n = isqrt(N)
primes = []
is_prime = [True] * (sqrt_n+1)
is_prime[0] = is_prime[1] = False

for p in range(2, sqrt_n+1):
    if not is_prime[p]:
        continue
    primes.append(p)
    for x in range(p, sqrt_n+1, p):
        is_prime[x] = False


cnt = 0
for i, p1 in enumerate(primes):
    if p1**4 > N:
        break
    if p1**8 <= N:
        cnt += 1
    for p2 in primes[i+1:]:
        if p1**2 * p2**2 > N:
            break
        cnt += 1
print(cnt)
