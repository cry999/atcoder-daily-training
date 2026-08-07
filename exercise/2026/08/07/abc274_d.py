# >>> atcoder-stat >>>
# started_at  = 2026-08-07T14:10:05+09:00
# solved_at   = 2026-08-07T14:21:48+09:00
# duration_ms = 703488
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, X, Y = map(int, input().split())
(*A,) = map(int, input().split())

sx = {A[0]}
for i in range(2, N, 2):
    sx = {x + A[i] for x in sx} | {x - A[i] for x in sx}

sy = {0}
for i in range(1, N, 2):
    sy = {y + A[i] for y in sy} | {y - A[i] for y in sy}

print("Yes" if X in sx and Y in sy else "No")
