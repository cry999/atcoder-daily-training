P = 10**4

primes = []
is_prime = [True] * (P + 1)
is_prime[0] = is_prime[1] = False

for p in range(2, P + 1):
    if not is_prime[p]:
        continue
    primes.append(p)
    for pp in range(p + p, P + 1, p):
        is_prime[pp] = False

N = int(input())
ans = 0
for _ in range(N):
    x = int(input())
    if x <= P:
        if is_prime[x]:
            ans += 1
        continue

    for p in primes:
        if p * p > x:
            ans += 1
            break
        if x == p:
            # is prime
            ans += 1
            break
        if x % p == 0:
            break
    else:
        ans += 1
print(ans)
