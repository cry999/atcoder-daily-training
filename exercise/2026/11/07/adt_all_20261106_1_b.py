# >>> atcoder-stat >>>
# started_at  = 2026-11-07T07:09:56+09:00
# solved_at   = 2026-11-07T07:11:08+09:00
# duration_ms = 72674
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
L1, R1, L2, R2 = map(int, input().split())
print(max(0, min(R1, R2) - max(L1, L2)))
