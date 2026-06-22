MOD = 10**9 + 7

N, K = map(int, input().split())

inv = [0] * (N + 1)
inv[1] = 1
for i in range(2, N + 1):
    q, r = divmod(MOD, i)
    inv[i] = (-inv[r] * q) % MOD

# {K-1}_C_{k-1}
comb_k_1 = [1] * K
for k in range(1, K):
    comb_k_1[k] = (comb_k_1[k - 1] * (K - k) * inv[k]) % MOD

# {N-K+1}_C_{k}
comb_n_k_1 = [1] * (K + 1)
for k in range(1, K + 1):
    comb_n_k_1[k] = (comb_n_k_1[k - 1] * (N - K - k + 2) * inv[k]) % MOD

for k in range(1, K + 1):
    print((comb_k_1[k - 1] * comb_n_k_1[k]) % MOD)
