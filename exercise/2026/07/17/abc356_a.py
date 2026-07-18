# >>> atcoder-stat >>>
# started_at  = 2026-07-17T18:34:19+09:00
# solved_at   = 2026-07-17T18:36:55+09:00
# duration_ms = 156711
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, L, R = map(int, input().split())
ans = [R + L - i if L <= i <= R else i for i in range(1, N + 1)]
print(*ans)
