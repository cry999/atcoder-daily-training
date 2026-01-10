N, K = map(int, input().split())

MOD = 998244353
inv_n = pow(N, MOD - 2, MOD)
p = 1
for _ in range(K):
    p = p * (N - 2) * inv_n + 2 * inv_n * inv_n
    p %= MOD

ans = p + (1 - p) * pow(N - 1, MOD - 2, MOD) * (N * (N + 1) * pow(2, MOD - 2, MOD) - 1)
print(ans % MOD)
