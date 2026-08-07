# >>> atcoder-stat >>>
# started_at  = 2026-08-04T10:12:04+09:00
# solved_at   = 2026-08-04T10:23:10+09:00
# duration_ms = 666774
# target_ms   = 900000
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

N, S = map(int, input().split())

dp = [-1] * (S + 1)
dp[0] = 0

for i in range(N):
    a, b = map(int, input().split())

    ndp = [-1] * (S + 1)
    for s in range(S + 1):
        if dp[s] == -1:
            continue
        if s + a <= S:
            ndp[s + a] = dp[s] | (1 << i)
        if s + b <= S:
            ndp[s + b] = dp[s] | (0 << i)

    dp = ndp

if dp[S] == -1:
    print("No")
else:
    print("Yes")

    ans = ""
    s = dp[S]
    for _ in range(N):
        ans += "H" if s & 1 else "T"
        s >>= 1
    print(ans)
