# >>> atcoder-stat >>>
# started_at  = 2026-08-07T15:06:13+09:00
# solved_at   = 2026-08-07T15:23:25+09:00
# duration_ms = 1032911
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
MOD = 998244353

S = input()
N = len(S)

# dp[n] := ) の個数が n 個の組み合わせ
dp = [0] * (N + 1)
dp[0] = 1

for i in range(N):
    ndp = [0] * (N + 1)
    if S[i] == "(":
        for c in range(N + 1):
            ndp[c] = dp[c]
    elif S[i] == ")":
        for c in range(N):
            if i + 1 >= 2 * (c + 1):
                ndp[c + 1] = dp[c]
    else:  # S[i] == '?'
        for c in range(N + 1):
            # ? -> (
            ndp[c] = dp[c]
            # ? -> )
            if c > 0 and i + 1 >= 2 * c:
                ndp[c] += dp[c - 1]

    dp = [x % MOD for x in ndp]
    print(f"[DEBUG] {i=}, {dp=}")

if N % 2 == 1:
    print(0)
else:
    print(f"[DEBUG] {dp=}")
    print(dp[N // 2])
