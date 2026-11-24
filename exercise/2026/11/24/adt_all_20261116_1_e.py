# >>> atcoder-stat >>>
# started_at  = 2026-11-24T07:05:00+09:00
# solved_at   = 2026-11-24T07:10:17+09:00
# duration_ms = 317866
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, M = map(int, input().split())
S = input()

parts = S.split("0")
max_len = max(len(part) for part in parts)
max_2 = max(part.count("2") for part in parts)

ans = max(max_len - M, max_2)
print(ans)
