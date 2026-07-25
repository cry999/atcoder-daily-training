# >>> atcoder-stat >>>
# started_at  = 2026-07-22T18:18:04+09:00
# solved_at   = 2026-07-22T18:24:02+09:00
# duration_ms = 358212
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
S = input()
N = len(S)

MOD = 10**9 + 7
# dp[S] := i 文字目まで、chokudai の並びの状況が S である部分列の個数。
dp = [0] * 9
dp[0] = 1

CHAR = "chokudai"

for i in range(N):
    ndp = dp[:]
    for j, c in enumerate(CHAR):
        if S[i] == c:
            ndp[j + 1] += dp[j]
    dp = [x % MOD for x in ndp]

print(dp[8])
