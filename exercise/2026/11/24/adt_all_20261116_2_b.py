# >>> atcoder-stat >>>
# started_at  = 2026-11-24T09:52:02+09:00
# solved_at   = 2026-11-24T09:54:19+09:00
# duration_ms = 137380
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
X, Y = map(int, input().split())
print(max(0, Y - X + 9) // 10)
