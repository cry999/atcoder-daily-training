# >>> atcoder-stat >>>
# started_at  = 2026-07-22T16:53:28+09:00
# solved_at   = 2026-07-22T16:56:54+09:00
# duration_ms = 206657
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, X = map(int, input().split())

dp = [False] * (X + 1)
dp[0] = True

for _ in range(N):
    a, b = map(int, input().split())

    ndp = [False] * (X + 1)
    for x in range(X):
        if x + a <= X:
            ndp[x + a] = ndp[x + a] or dp[x]
        if x + b <= X:
            ndp[x + b] = ndp[x + b] or dp[x]

    dp = ndp

print("Yes" if dp[X] else "No")
