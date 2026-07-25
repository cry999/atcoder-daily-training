# >>> atcoder-stat >>>
# started_at  = 2026-07-22T18:44:13+09:00
# solved_at   = 2026-07-22T18:49:01+09:00
# duration_ms = 288754
# target_ms   = 900000
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
    ndp = [False] * (X + 1)
    max_j = [-1] * (X + 1)

    a, b = map(int, input().split())
    for x in range(X, -1, -1):
        if dp[x]:
            for y in range(x, min(X, x + a * b) + 1, a):
                if ndp[y]:
                    continue
                ndp[y] = ndp[y] or dp[x]

    dp = ndp

print("Yes" if dp[X] else "No")
