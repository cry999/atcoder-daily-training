# >>> atcoder-stat >>>
# duration_ms = 520000
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
S = [input() for _ in range(5)]

RED = 0
BLUE = 1
WHITE = 2

# i 列目を赤・青・白に塗る時の最小手数
dp = [0] * 3
for i in range(5):
    dp[RED] += S[i][0] != "R"
    dp[BLUE] += S[i][0] != "B"
    dp[WHITE] += S[i][0] != "W"


for i in range(1, N):
    ndp = [min(dp[j] for j in range(3) if i != j) for i in range(3)]

    for j in range(5):
        ndp[RED] += S[j][i] != "R"
        ndp[BLUE] += S[j][i] != "B"
        ndp[WHITE] += S[j][i] != "W"

    dp = ndp

print(min(dp))
