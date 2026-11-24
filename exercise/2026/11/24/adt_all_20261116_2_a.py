# >>> atcoder-stat >>>
# started_at  = 2026-11-24T09:50:52+09:00
# solved_at   = 2026-11-24T09:51:58+09:00
# duration_ms = 66094
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())
(*A,) = map(int, input().split())
(*B,) = filter(lambda x: x % 2 == 0, A)
print(*B)
