# >>> atcoder-stat >>>
# started_at  = 2026-08-07T15:55:15+09:00
# solved_at   = 2026-08-07T16:01:23+09:00
# duration_ms = 368827
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, K, D = map(int, input().split())
(*A,) = map(int, input().split())

# dp[k][d] := A の k この項の和で D で割ったあまりが d になる最大の数
dp = [[-1] * D for _ in range(K + 1)]
dp[0][0] = 0

for a in A:
    for k in range(K - 1, -1, -1):
        for d in range(D):
            if dp[k][d] == -1:
                continue
            n = dp[k][d] + a
            dp[k + 1][n % D] = max(dp[k + 1][n % D], n)

print(f"[DEBUG] {dp=}")
print(dp[K][0])
