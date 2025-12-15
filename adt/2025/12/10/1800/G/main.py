import os
import sys


DEBUG = os.getenv('DEBUG', '0') == '1'
MOD = 998244353


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs, file=sys.stderr)


N = int(input())
*A, = map(int, input().split())

ans = 0
for i in range(1, N+1):
    debug(f'=== i: {i} ===')
    # dp[j][k][l] := A の j 番目までの項目から k 個選んだ総和を i で割ったあまりが l になる個数。
    dp = [[[0]*i for _ in range(i+1)] for _ in range(N+1)]
    dp[0][0][0] = 1
    for j in range(N):
        # j 番目までの項目からは j 個までしか選べない。
        # また、全体の最大個数は i 個までしか選べない。
        for k in range(i+1):
            for l in range(i):
                # A[j] を選ばない場合
                dp[j+1][k][l] += dp[j][k][l]
                dp[j+1][k][l] %= MOD
                # A[j] を選ぶ場合
                if k < i:
                    dp[j+1][k+1][(l+A[j]) % i] += dp[j][k][l]
                    dp[j+1][k+1][(l+A[j]) % i] %= MOD
    debug(dp)
    ans += dp[N][i][0]
    ans %= MOD
print(ans)
