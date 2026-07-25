# >>> atcoder-stat >>>
# started_at  = 2026-07-22T18:04:03+09:00
# solved_at   = 2026-07-22T18:17:35+09:00
# duration_ms = 812940
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())
(*A,) = map(int, input().split())
M = int(input())
(*B,) = map(int, input().split())
X = int(input())

# dp[i] := i 段目にロボットは辿り着けるか?!
dp = [0] * (X + 1)
dp[0] = 1
for forbidden in B:
    dp[forbidden] = -1

for i in range(X):
    if dp[i] <= 0:
        continue
    for step in A:
        if i + step > X:
            continue
        if dp[i + step] < 0:
            continue
        dp[i + step] = max(dp[i], dp[i + step])

print("Yes" if dp[X] > 0 else "No")
