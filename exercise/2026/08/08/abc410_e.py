# >>> atcoder-stat >>>
# started_at  = 2026-08-08T08:58:42+09:00
# solved_at   = 2026-08-08T09:07:28+09:00
# duration_ms = 526922
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline
N, H, M = map(int, input().split())

# dp[h] := 体力の残りが h の時の最大残存魔力
dp = [0] * (H + 1)
dp[H] = M

ans = 0
for i in range(N):
    use_hitpoint, use_magicpoint = map(int, input().split())

    ndp = [0] * (H + 1)
    for h in range(H + 1):
        ndp[h] = dp[h] - use_magicpoint
        if h + use_hitpoint <= H:
            ndp[h] = max(ndp[h], dp[h + use_hitpoint])

    if all(x < 0 for x in ndp):
        break

    dp = ndp
    ans = i + 1
print(ans)
