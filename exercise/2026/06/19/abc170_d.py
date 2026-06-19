from collections import Counter

N = int(input())
(*A,) = map(int, input().split())
A.sort()
counter = Counter(A)

M = 10**6
is_prime = [True] * (M + 1)
primes = []

for a in A:
    if not is_prime[a]:
        continue

    if counter[a] == 1:
        primes.append(a)
    else:
        is_prime[a] = False

    for i in range(a * 2, M + 1, a):
        is_prime[i] = False

print(len(primes))
