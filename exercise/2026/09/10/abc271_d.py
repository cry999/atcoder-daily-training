# >>> atcoder-stat >>>
# started_at  = 2026-09-10T10:50:38+09:00
# solved_at   = 2026-09-10T10:57:32+09:00
# duration_ms = 414645
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
dp = [[0] * (S + 1) for _ in range(N + 1)]
dp[0][0] = 1

cards = []
for i in range(N):
    a, b = map(int, input().split())
    for s in range(S + 1):
        if s + a > S and s + b > S:
            break
        if not dp[i][s]:
            continue
        if s + a <= S:
            dp[i + 1][s + a] = 1
        if s + b <= S:
            dp[i + 1][s + b] = 1
    cards.append((a, b))

if dp[N][S]:
    print("Yes")
    s = S
    ans = [""] * N
    for i in range(N - 1, -1, -1):
        a, b = cards[i]
        if s - a >= 0 and dp[i][s - a]:
            s -= a
            ans[i] = "H"
        else:
            s -= b
            ans[i] = "T"
    print("".join(ans))
else:
    print("No")
