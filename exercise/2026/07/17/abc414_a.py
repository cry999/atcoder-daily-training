# >>> atcoder-stat >>>
# started_at  = 2026-07-17T18:32:15+09:00
# solved_at   = 2026-07-17T18:37:20+09:00
# duration_ms = 305499
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, L, R = map(int, input().split())

ans = 0
for _ in range(N):
    X, Y = map(int, input().split())
    if X <= L and R <= Y:
        ans += 1
print(ans)
