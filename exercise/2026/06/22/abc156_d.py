MOD = 10**9 + 7

n, a, b = map(int, input().split())

N = 2 * 10**5
inv = [0] * (N + 1)
inv[1] = 1

for i in range(2, N + 1):
    q, r = divmod(MOD, i)
    inv[i] = (-inv[r] * q) % MOD


comb = [1] * (N + 1)
for r in range(1, min(n, N) + 1):
    comb[r] = (comb[r - 1] * (n - r + 1) * inv[r]) % MOD


ans = pow(2, n, MOD) - 1 - comb[a] - comb[b]
print(ans % MOD)
