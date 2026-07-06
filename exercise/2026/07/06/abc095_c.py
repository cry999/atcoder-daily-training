# >>> atcoder-stat >>>
# started_at  = 2026-07-06T11:43:44+09:00
# solved_at   = 2026-07-06T11:49:33+09:00
# duration_ms = 349981
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<

A, B, C, X, Y = map(int, input().split())

price = A * X + B * Y
ans = price

for i in range(max(X, Y)):
    if i < X:
        price -= A
    if i < Y:
        price -= B
    price += C * 2
    ans = min(ans, price)
print(ans)
