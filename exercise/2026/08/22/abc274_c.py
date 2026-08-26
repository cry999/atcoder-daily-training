# >>> atcoder-stat >>>
# started_at  = 2026-08-22T20:54:34+09:00
# solved_at   = 2026-08-22T20:59:55+09:00
# duration_ms = 321291
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())
(*A,) = map(int, input().split())

gen = [0] * (2 * N + 2)
for i in range(N):
    nxt1 = 2 * (i + 1)
    nxt2 = 2 * (i + 1) + 1
    gen[nxt1] = gen[A[i]] + 1
    gen[nxt2] = gen[A[i]] + 1

for i in range(1, 2 * N + 2):
    print(gen[i])
