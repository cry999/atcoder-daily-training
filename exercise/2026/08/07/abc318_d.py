# >>> atcoder-stat >>>
# started_at  = 2026-08-07T15:46:25+09:00
# solved_at   = 2026-08-07T15:55:05+09:00
# duration_ms = 520253
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())
D = [list(map(int, input().split())) for _ in range(N - 1)]

# dp[s] := ノードの集合 s に対する最大値
dp = [0] * (1 << N)
for s in range(1 << N):
    for i in range(N):
        if s & (1 << i):
            continue
        for j in range(i + 1, N):
            if s & (1 << j):
                continue
            d = D[i][j - i - 1]
            ns = s | (1 << i) | (1 << j)
            dp[ns] = max(dp[ns], dp[s] + d)

ALL = (1 << N) - 1
print(dp[ALL])
