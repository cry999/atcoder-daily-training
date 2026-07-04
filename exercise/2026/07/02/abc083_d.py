# >>> atcoder-stat >>>
# started_at  = 2026-07-02T14:53:01+09:00
# solved_at   = 2026-07-02T16:11:12+09:00
# duration_ms = 4691733
# target_ms   = 900000
# ac          = true
# editorial   = true
# knowledge   = 2
# translation = 2
# complexity  = 1
# impl        = 1
# verify      = 2
# <<< atcoder-stat <<<
S = input()
N = len(S)

ans = N
for i in range(N - 1):
    if S[i] != S[i + 1]:
        ans = min(ans, max(i + 1, N - i - 1))
print(ans)
