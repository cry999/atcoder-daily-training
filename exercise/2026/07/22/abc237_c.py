# >>> atcoder-stat >>>
# started_at  = 2026-07-22T16:11:40+09:00
# solved_at   = 2026-07-22T16:16:42+09:00
# duration_ms = 302982
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
S = input()
N = len(S)
i, j = 0, N - 1
while 0 <= i < j < N and S[j] == "a":
    if S[i] == "a":
        i += 1
    j -= 1

while 0 <= i < j < N and S[i] == S[j]:
    i += 1
    j -= 1

if i >= j:
    print("Yes")
else:
    print("No")
