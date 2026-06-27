MAX_N = 55_555

is_prime = [True] * (MAX_N + 1)
is_prime[0] = is_prime[1] = False

primes = []

for p in range(2, MAX_N + 1):
    if not is_prime[p]:
        continue

    primes.append(p)
    for pp in range(2 * p, MAX_N + 1, p):
        is_prime[pp] = False

N = int(input())
ans = []
i = 0
while len(ans) < N:
    if primes[i] % 5 == 1:
        ans.append(primes[i])
    i += 1
print(*ans)
