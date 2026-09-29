# >>> atcoder-stat >>>
# started_at  = 2026-09-29T14:19:59+09:00
# solved_at   = 2026-09-29T14:47:06+09:00
# duration_ms = 1627497
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 1
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
N, K = map(int, input().split())

MOD = 10**9 + 7

# 考察
# 1. 人数の合計は N 人
# 2. 人が誰もいない部屋が K 個以下
# 3. 両方を満たす人数の配置の仕方を考える。
# 4. 人が誰もいない部屋が k 個の時、選び方は comb(N, k) 通り
# 5. N-k の部屋に空きなく N 人を配置するので、comb(N-1, N-k-1) 通り
# 6, つまり、k を 0 から min(K, N-1)まで動かしながら comb(N, k) * comb(N-1, N-k-1) を足し合わせる。

# comb1[k] := comb(N, k)
comb1 = [1] * (N + 1)
# comb2[k] := comb(N-1, k)
comb2 = [1] * N

inv = [1] * (N + 1)
for i in range(2, N + 1):
    q, r = divmod(MOD, i)
    inv[i] = -q * inv[r] % MOD

for i in range(1, N + 1):
    comb1[i] = comb1[i - 1] * (N - i + 1) % MOD * inv[i] % MOD
for i in range(1, N):
    comb2[i] = comb2[i - 1] * (N - i) % MOD * inv[i] % MOD

ans = 0
for k in range(min(K, N - 1) + 1):
    ans += comb1[k] * comb2[N - k - 1]
    ans %= MOD
print(ans)
