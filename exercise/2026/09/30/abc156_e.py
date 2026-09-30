# >>> atcoder-stat >>>
# started_at  = 2026-09-30T09:10:29+09:00
# solved_at   = 2026-09-30T09:25:33+09:00
# duration_ms = 904648
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
MOD = 10**9 + 7


N, K = map(int, input().split())

# 考察
# 1. 人が k 回移動するということは、人のいない部屋が高々 k 個存在するということ
# 2. k この部屋が空であるとすると、
# 3. 空になる部屋の選び方が comb(N, k) 通り
# 4. 残りの N-k 個の部屋に空きを出さずに N 人を配置する方法が comb(N-1, N-k-1)
# 5. k の範囲は [0, min(K, N-1)]

inv = [1] * (N + 1)
for i in range(2, N + 1):
    q, r = divmod(MOD, i)
    inv[i] = -q * inv[r] % MOD

comb1 = [1] * (N + 1)
for i in range(1, N + 1):
    comb1[i] = comb1[i - 1] * (N - i + 1) * inv[i] % MOD

comb2 = [1] * N
for i in range(1, N):
    comb2[i] = comb2[i - 1] * (N - i) * inv[i] % MOD

ans = 0
for k in range(min(K, N - 1) + 1):
    ans += comb1[k] * comb2[N - k - 1] % MOD
    ans %= MOD
print(ans)
