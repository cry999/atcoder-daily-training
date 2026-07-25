# >>> atcoder-stat >>>
# started_at  = 2026-07-23T07:28:05+09:00
# solved_at   = 2026-07-23T07:31:37+09:00
# duration_ms = 212426
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, X, Y = map(int, input().split())

R, B = 1, 0

for _ in range(N - 1):
    B += X * R
    R += B
    B = Y * B

print(B)
