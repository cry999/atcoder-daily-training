# >>> atcoder-stat >>>
# started_at  = 2026-08-29T20:01:41+09:00
# solved_at   = 2026-08-29T20:14:58+09:00
# duration_ms = 797720
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 2
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline


N = int(input())

parts = [tuple(map(int, input().split())) for _ in range(N)]
S = sum(w for w, _, _ in parts)
B = sum(b for _, _, b in parts)

M = S // 2
# dp[x] := 頭の重さがちょうど x の時の最大価値
dp = [-1] * (M + 1)
dp[0] = 0

cur_max = 0
for w, h, b in parts:
    if h <= b:
        continue

    for x in range(min(cur_max, M - w), -1, -1):
        if dp[x] < 0:
            continue
        dp[x + w] = max(dp[x + w], dp[x] + h - b)

    cur_max = min(cur_max + w, M)

print(max(dp) + B)
