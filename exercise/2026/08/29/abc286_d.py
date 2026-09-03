# >>> atcoder-stat >>>
# started_at  = 2026-08-29T19:43:39+09:00
# solved_at   = 2026-08-29T19:47:53+09:00
# duration_ms = 254649
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


N, X = map(int, input().split())

dp = [False] * (X + 1)
dp[0] = True

INF = 10**18
max_j = [-INF] * (X + 1)
for _ in range(N):
    a, b = map(int, input().split())

    # 前計算: max_j[j] := j, j-a, j-2a, ... の内 dp[j'] = True となる最大の j
    for j in range(X + 1):
        if dp[j]:
            max_j[j] = j
        elif j - a >= 0:
            max_j[j] = max_j[j - a]
        else:
            max_j[j] = -INF

    print(f"[DEBUG] {max_j=}")
    # for x in range(X - a, -1, -1):
    for x in range(X + 1):
        # if not dp[x]:
        #     continue
        # for y in range(1, b + 1):
        #     if x + a * y > X:
        #         break
        #     dp[x + a * y] = True
        print(f"[DEBUG] {x=}, {max_j[x]=}, {a=}, {b=}")
        dp[x] = max_j[x] >= x - a * b
    if dp[X]:
        print("Yes")
        break
    print(f"[DEBUG] {dp=}")
else:
    print("No")
print(f"[DEBUG] {dp=}")
