# >>> atcoder-stat >>>
# started_at  = 2026-10-02T11:45:47+09:00
# solved_at   = 2026-10-02T12:21:39+09:00
# duration_ms = 2152718
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 1
# complexity  = 3
# impl        = 1
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())
(*A,) = map(int, input().split())

# dp[l] := l 個左に置いたときの最大スコア
dp = [0]

# 活発度の高い順におく。
order = sorted(((a, i) for i, a in enumerate(A)), reverse=True)
for k, (a, i) in enumerate(order):
    ndp = [-1] * (k + 2)

    for l in range(k + 1):
        score = dp[l]
        r = N - 1 - (k - l)  # 絶対位置

        # 左に置く: 左の人数 l -> l+1
        ndp[l + 1] = max(ndp[l + 1], score + a * abs(i - l))
        # 右に置く: 左の人数は変わらない。
        ndp[l] = max(ndp[l], score + a * abs(i - r))

    dp = ndp

print(max(dp))
