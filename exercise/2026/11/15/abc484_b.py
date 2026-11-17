# >>> atcoder-stat >>>
# started_at  = 2026-11-15T09:17:10+09:00
# solved_at   = 2026-11-15T09:18:33+09:00
# duration_ms = 83228
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
K = int(input())
(*A,) = map(int, input().split())
if max(A) == 9:
    print(min(A))
else:
    print(-1)
