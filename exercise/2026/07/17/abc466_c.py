# >>> atcoder-stat >>>
# started_at  = 2026-07-17T19:51:30+09:00
# solved_at   = 2026-07-17T19:55:41+09:00
# duration_ms = 251002
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())

j = 1
ans = 0
for i in range(1, N):
    j = max(j, i + 1)
    while j <= N:
        print("?", i, j)
        if input() == "Yes":
            j += 1
        else:
            break
    ans += j - i - 1
print("!", ans)
