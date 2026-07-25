# >>> atcoder-stat >>>
# started_at  = 2026-07-22T16:35:36+09:00
# solved_at   = 2026-07-22T16:52:37+09:00
# duration_ms = 1021062
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, X, Y = map(int, input().split())

R = [0] * (N + 1)
B = [0] * (N + 1)
R[N] = 1

for n in range(N, 1, -1):
    B[n] += X * R[n]
    R[n - 1] = R[n] + B[n]
    B[n - 1] += Y * B[n]

print(B[1])
