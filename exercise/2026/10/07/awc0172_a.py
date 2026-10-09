# >>> atcoder-stat >>>
# started_at  = 2026-10-07T06:26:24+09:00
# solved_at   = 2026-10-07T06:27:29+09:00
# duration_ms = 65523
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())
for _ in range(N):
    a, b = map(int, input().split())
    print((a + b) % 24)
