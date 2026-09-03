# >>> atcoder-stat >>>
# started_at  = 2026-09-04T05:43:25+09:00
# solved_at   = 2026-09-04T05:49:13+09:00
# duration_ms = 348105
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, X, Y = map(int, input().split())
(*A,) = map(int, input().split())

last_invalid, last_x, last_y = -1, -1, -1
ans = 0
for r, a in enumerate(A):
    if a == X:
        last_x = r
    if a == Y:
        last_y = r
    if not (Y <= a <= X):
        last_invalid = r

    ans += max(0, min(last_x, last_y) - last_invalid)

print(ans)
