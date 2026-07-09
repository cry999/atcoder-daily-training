# >>> atcoder-stat >>>
# started_at  = 2026-07-10T06:04:45+09:00
# solved_at   = 2026-07-10T06:13:53+09:00
# duration_ms = 548898
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
X, Y = map(int, input().split())

if (X + Y) % 3 != 0:
    print(0)
    exit()

N = (X + Y) // 3
NY = (-X + 2 * Y) // 3
NX = (2 * X - Y) // 3

if NY < 0 or NX < 0:
    print(0)
    exit()

MOD = 10**9 + 7

inv = [1] * (N + 1)
for i in range(2, N + 1):
    q, r = divmod(MOD, i)
    inv[i] = (-q * inv[r]) % MOD

M = min(NY, NX)
comb = [1] * (M + 1)
for r in range(1, M + 1):
    comb[r] = (comb[r - 1] * (N - r + 1) * inv[r]) % MOD
print(comb[M])
