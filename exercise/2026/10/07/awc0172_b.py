# >>> atcoder-stat >>>
# started_at  = 2026-10-07T06:55:15+09:00
# solved_at   = 2026-10-07T06:56:37+09:00
# duration_ms = 82378
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
H, W = map(int, input().split())
S = [input() for _ in range(H)]
print(max(s.count("x") for s in S))
