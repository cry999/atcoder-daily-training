from math import isqrt

N = int(input())

MAX_PRIME = max(isqrt(N // 4), 10)

primes = []
is_prime = [True] * (MAX_PRIME + 1)
is_prime[0] = is_prime[1] = False

for p in range(2, MAX_PRIME + 1):
    if not is_prime[p]:
        continue
    primes.append(p)
    for d in range(1, MAX_PRIME // p + 1):
        is_prime[p * d] = False

cnt = 0
for i in range(len(primes)):
    p1 = primes[i]
    if p1**8 <= N:
        cnt += 1

    # if p1**4 > N:
    #     break

    for j in range(i + 1, len(primes)):
        p2 = primes[j]
        if p1**2 * p2**2 > N:
            break
        cnt += 1

print(cnt)
