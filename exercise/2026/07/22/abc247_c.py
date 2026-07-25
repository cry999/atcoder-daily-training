# >>> atcoder-stat >>>
# started_at  = 2026-07-22T16:07:28+09:00
# solved_at   = 2026-07-22T16:11:17+09:00
# duration_ms = 180000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())
S = [""] * N
S[0] = "1"
for i in range(1, N):
    S[i] = f"{S[i-1]} {i+1} {S[i-1]}"
print(S[-1])
