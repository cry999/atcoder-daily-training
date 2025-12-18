import os
import sys

MOD = 998244353
DEBUG = os.environ.get("DEBUG", "0") == "1"


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs, file=sys.stderr)


memo = {}


def comb(n: int, r: int) -> int:
    if r == 0 or n == r:
        return 1
    r = min(n-r, r)
    key = (n, r)
    if key in memo:
        return memo[key]

    # 今回は (n, r) の前に (n, r-1) は計算されているはずなので
    memo[key] = comb(n, r-1) * (n-r+1) * pow(r, MOD-2, MOD)
    memo[key] %= MOD
    return memo[key]


K = int(input())
*C, = map(int, input().split())

dp = [[0]*(K+1) for _ in range(26+1)]

dp[0][0] = 1

for i in range(26):
    if C[i] == 0:
        dp[i+1] = dp[i][:]
        continue
    debug(f'i={i}, C[i]={C[i]}')
    for k in range(K+1):
        debug(f'  k={k}, dp[{i}][{k}]={dp[i][k]}')
        x = min(k, C[i])
        debug(f'  x={x}')
        for j in range(x+1):
            # debug(f'    {j=}, {comb(k, j)=}, dp[{i}][{k-j}]={dp[i][k-j]}')
            dp[i+1][k] += (comb(k, j) * dp[i][k-j]) % MOD
            dp[i+1][k] %= MOD

print(sum(dp[-1][1:]) % MOD)
