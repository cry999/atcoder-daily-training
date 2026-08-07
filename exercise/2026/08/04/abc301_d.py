# >>> atcoder-stat >>>
# started_at  = 2026-08-04T09:36:01+09:00
# solved_at   = 2026-08-04T10:08:30+09:00
# duration_ms = 1949036
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
S = input().rjust(60, "0")
N = int(input())
T = bin(N)[2:].rjust(60, "0")

dp = [0, -1]

for i in range(60):
    if S[i] == "?":
        dp[:] = (
            max(-1, dp[0] * 2 + int(T[i])),
            max(dp[1] * 2 + 1, dp[0] * 2 if T[i] == "1" else -1),
        )
    else:
        if T[i] == S[i]:
            dp[:] = (
                max(-1, dp[0] * 2 + int(S[i])),
                max(-1, dp[1] * 2 + int(S[i])),
            )

        elif T[i] == "1" and S[i] == "0":
            dp[:] = (
                -1,
                max(-1, max(dp) * 2 + 0),
            )
        else:
            dp[:] = (
                -1,
                max(-1, dp[1] * 2 + 1),
            )
    print(f"[DEBUG] {S[i]=} {T[i]=} :{dp}")
print(max(dp))
