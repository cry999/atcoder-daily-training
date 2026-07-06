# >>> atcoder-stat >>>
# started_at  = 2026-07-06T11:31:08+09:00
# solved_at   = 2026-07-06T11:33:54+09:00
# duration_ms = 166897
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())

ans = 0
for n in range(1, N + 1, 2):
    div = 2
    for d in range(2, n):
        if d * d > n:
            break
        if n % d == 0:
            if d * d == n:
                div += 1
            else:
                div += 2
    if div == 8:
        ans += 1
print(ans)
