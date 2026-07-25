# >>> atcoder-stat >>>
# started_at  = 2026-07-23T11:04:30+09:00
# solved_at   = 2026-07-23T11:30:31+09:00
# duration_ms = 1561715
# target_ms   = 900000
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 2
# complexity  = 2
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())

parts = [tuple(map(int, input().split())) for _ in range(N)]
# 頭につけたほうが良いものを floor(s / 2) 以下の重さで最大化する
INF = float("inf")
M = sum(w for w, _, _ in parts) // 2
dp = [-INF] * (M + 1)
dp[0] = sum(b for _, _, b in parts)
for w, h, b in parts:
    for k in range(M, -1, -1):
        # head に移動する。移動なので、body に計上していた分を減らして -b が発生する。
        if h > b and k + w <= M:
            dp[k + w] = max(dp[k + w], dp[k] + h - b)

ans = max(dp)
print(ans)
