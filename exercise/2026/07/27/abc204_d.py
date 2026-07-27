# >>> atcoder-stat >>>
# started_at  = 2026-07-27T21:41:18+09:00
# solved_at   = 2026-07-27T21:51:24+09:00
# duration_ms = 606230
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
(*T,) = map(int, input().split())

S = sum(T)

# dp[t] := t を実現できるか？
dp = [0] * (S // 2 + 1)
dp[0] = 1

for t in T:
    for j in range(S // 2 - t, -1, -1):
        dp[j + t] |= dp[j]

for j in range(S // 2, -1, -1):
    if dp[j]:
        print(S - j)
        break
