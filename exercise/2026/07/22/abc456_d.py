# >>> atcoder-stat >>>
# started_at  = 2026-07-22T18:24:13+09:00
# solved_at   = 2026-07-22T18:33:28+09:00
# duration_ms = 555062
# target_ms   = 900000
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

MOD = 998244353

# dp[c] := c 以外の文字が右端にある部分列の個数
dp = [0] * 3

for i in range(N):
    ndp = [0] * 3
    for c in range(3):
        if chr(c + ord("a")) == S[i]:
            ndp[c] = sum(dp) + 1
        else:
            ndp[c] = dp[c]
    dp = [x % MOD for x in ndp]
    # print(dp)

print(sum(dp) % MOD)
