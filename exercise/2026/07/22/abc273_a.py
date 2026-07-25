# >>> atcoder-stat >>>
# started_at  = 2026-07-22T15:48:13+09:00
# solved_at   = 2026-07-22T15:50:23+09:00
# duration_ms = 130593
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())
f = [0] * (N + 1)
f[0] = 1
for i in range(N):
    f[i + 1] = f[i] * (i + 1)
print(f[N])
