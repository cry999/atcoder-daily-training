import os
import sys


DEBUG = os.getenv('DEBUG', '0') == '1'


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs, file=sys.stderr)


if DEBUG:
    from fractions import Fraction


MOD = 998244353
N, M, K = map(int, input().split())

# ルーレットの各目が出る確率
P = pow(M, MOD-2, MOD)
if DEBUG:
    P = Fraction(1, M)

# dp[i][j%2] = j 回目の操作で i にいる確率
dp = [[0] * (N+1) for _ in range(2)]
dp[0][0] = 1

ans = 0
for j in range(K):
    for i in range(N+1):
        dp[(j+1) % 2][i] = 0
    for i in range(N):
        if dp[j % 2][i] == 0:
            continue
        for d in range(1, M+1):
            ni = i+d
            if ni > N:
                ni = N-(ni-N)
            dp[(j+1) % 2][ni] += P*dp[j % 2][i]
            if not DEBUG:
                dp[(j+1) % 2][ni] %= MOD

    ans += dp[(j+1) % 2][N]
    if DEBUG:
        debug(' | '.join(map(str, dp[(j+1) % 2])))
    else:
        ans %= MOD
print(ans)
