# >>> atcoder-stat >>>
# duration_ms = 1380000
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
def f(n: int):
    return n * (n + 1) * (n + 2) // 6


INF = 10**18
dp1 = [INF] * (10**6 + 1)
dp1[0] = 0
dp2 = [INF] * (10**6 + 1)
dp2[0] = 0
for n in range(1, 182):
    m = f(n)
    for k in range(m, 10**6 + 1):
        dp1[k] = min(dp1[k], dp1[k - m] + 1)
        if m % 2:
            dp2[k] = min(dp2[k], dp2[k - m] + 1)

while True:
    N = int(input())
    if N == 0:
        break
    print(dp1[N], dp2[N])
