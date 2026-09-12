# >>> atcoder-stat >>>
# started_at  = 2026-09-11T14:10:45+09:00
# solved_at   = 2026-09-11T14:26:25+09:00
# duration_ms = 940660
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline


# NOTE: どの 2 変数を利用して DP を行うか

INF = 10**18

N, X, Y = map(int, input().split())
# dp[i][x] := i この料理で甘さが x となる時の最小のしょっぱさ
dp = [[INF] * (X + 1) for _ in range(N + 1)]
dp[0][0] = 0
for n in range(N):
    a, b = map(int, input().split())
    for i in range(n, -1, -1):
        for x in range(a, X + 1):
            dp[i + 1][x] = min(dp[i + 1][x], dp[i][x - a] + b)
print(f"[DEBUG] {dp=}")
ans = 0
for i in range(N, -1, -1):
    for x in range(X + 1):
        if dp[i][x] <= Y:
            # X, Y どちらかを超えるまで選んで良いので、
            # sum(A) <= X かつ sum(B) <= Y である最大の選び方に
            # なんでも良いから 1 つ追加で選んでいい。
            ans = min(max(ans, i + 1), N)
            break
    else:
        continue
    break
print(ans)
