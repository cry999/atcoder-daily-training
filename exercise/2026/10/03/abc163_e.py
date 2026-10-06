# >>> atcoder-stat >>>
# started_at  = 2026-10-03T12:55:19+09:00
# solved_at   = 2026-10-03T13:04:28+09:00
# duration_ms = 549201
# ac          = true
# editorial   = true
# knowledge   = 2
# translation = 1
# complexity  = 3
# impl        = 1
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())
(*A,) = map(int, input().split())

# 考察
# 1. A[i] が大きいものをできるだけ遠くにやった方が良い?
# 2. A[i] を x だけ動かすと、A[i] * x 点スコアが増える。
# 3. なので、A[i] が大きいものをできるだけ遠くにやるので良い。
# 4. dp[l] := l 個左に置いた時の最大スコア

dp = [0]
order = sorted(range(N), key=lambda i: -A[i])

for k, i in enumerate(order):
    ndp = [-1] * (k + 2)

    for l in range(k + 1):
        score = dp[l]
        r = N - 1 - (k - l)

        ndp[l + 1] = max(ndp[l + 1], score + A[i] * abs(i - l))
        ndp[l] = max(ndp[l], score + A[i] * abs(r - i))

    dp[:] = ndp[:]

print(max(dp))
