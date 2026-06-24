N = int(input())

primes = []
is_prime = [True] * (N + 1)
is_prime[0] = is_prime[1] = False

for i in range(2, N + 1):
    if not is_prime[i]:
        continue
    primes.append(i)
    for p in range(i * 2, N + 1, i):
        is_prime[i] = False

M = len(primes)
# f: N! の素因数分解
f = [0] * (M + 1)
for n in range(2, N + 1):
    for i, p in enumerate(primes):
        while n % p == 0:
            f[i] += 1
            n //= p

ans = 0
for i in range(M):
    if f[i] >= 74:
        print(f"[DEBUG] {i=}(74): {f[i]=}")
        ans += 1

    for j in range(M):
        if i == j:
            continue

        if f[i] >= 24 and f[j] >= 2:
            print(f"[DEBUG] {i=}(24), {j=}(2): {f[i]=}, {f[j]=}")
            ans += 1
        if f[i] >= 14 and f[j] >= 4:
            print(f"[DEBUG] {i=}(14), {j=}(4): {f[i]=}, {f[j]=}")
            ans += 1

        for k in range(j + 1, M):
            if k == i:
                continue

            if f[i] >= 2 and f[j] >= 4 and f[k] >= 4:
                ans += 1
print(ans)
