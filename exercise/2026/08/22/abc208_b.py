# >>> atcoder-stat >>>
# started_at  = 2026-08-22T20:51:03+09:00
# solved_at   = 2026-08-22T20:53:48+09:00
# duration_ms = 165155
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
P = int(input())

coin = 1
for i in range(1, 11):
    coin *= i


ans = 0
for i in range(10, 0, -1):
    while P >= coin:
        P -= coin
        ans += 1
    coin //= i
print(ans)
