# >>> atcoder-stat >>>
# started_at  = 2026-11-24T07:00:46+09:00
# solved_at   = 2026-11-24T07:04:55+09:00
# duration_ms = 249144
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, K = map(int, input().split())
S = input()

t: list[str] = []
k = 0
for s in S:
    if s == "o" and k < K:
        t.append(s)
        k += 1
    else:
        t.append("x")

print("".join(t))
