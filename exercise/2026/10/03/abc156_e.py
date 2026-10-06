# >>> atcoder-stat >>>
# started_at  = 2026-10-03T11:41:38+09:00
# solved_at   = 2026-10-03T11:50:23+09:00
# duration_ms = 525685
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
# 1. ちょうど K 回の移動 == K 個以下の空き部屋
# 2. sum(空き部屋が k 個の時の人の配置 for k in range(K + 1))
# 3. 空き部屋が k 個の時の人の配置 = 空き部屋の選び方 x N 人を N-k 個の部屋に分ける方法
# 4. 答えは各部屋にいる人の数の組み合わせなので、部屋は区別して、人は区別しない
# 5. 空き部屋の選び方 = comb(N, k)
# 6. 区別しない N 人を区別する N-k この部屋に 1 人以上配置する方法 = comb(N-1, N-k-1)

inv = [1] * (N + 1)
for i in range(2, N + 1):
    q, r = divmod(MOD, i)
    inv[i] = -q * inv[r] % MOD

comb1 = [1] * (N + 1)
for k in range(1, N + 1):
    comb1[k] = comb1[k - 1] * (N - k + 1) % MOD * inv[k] % MOD

comb2 = [1] * N
for k in range(1, N):
    comb2[k] = comb2[k - 1] * (N - k) % MOD * inv[k] % MOD

ans = sum(comb1[k] * comb2[N - k - 1] % MOD for k in range(min(K, N - 1) + 1)) % MOD
print(ans)
