# >>> atcoder-stat >>>
# started_at  = 2026-11-24T13:09:30+09:00
# solved_at   = 2026-11-24T13:11:21+09:00
# duration_ms = 111821
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
X = sorted(input())
for i in range(len(X)):
    if X[i] != "0":
        X[0], X[i] = X[i], X[0]
        break
print("".join(X))
