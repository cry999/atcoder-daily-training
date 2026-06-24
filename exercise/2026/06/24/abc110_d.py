from math import isqrt

MOD = 10**9 + 7
N, M = map(int, input().split())


facts = []
for i in range(2, isqrt(M) + 1):
    if M % i:
        continue

    n = 0
    while M % i == 0:
        M //= i
        n += 1

    facts.append(n)
if M > 1:
    facts.append(1)

P = max(facts or [1])
comb = [0] * (P + 1)
comb[0] = 1
inv = [0] * (P + 1)
inv[1] = 1

for k in range(1, P + 1):
    if k > 1:
        q, r = divmod(MOD, k)
        inv[k] = (-inv[r] * q) % MOD
    comb[k] = ((k + N - 1) * inv[k] * comb[k - 1]) % MOD

ans = 1
for n in facts:
    ans *= comb[n]
    ans %= MOD

print(ans)
