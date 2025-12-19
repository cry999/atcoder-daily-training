from collections import defaultdict
import os
import sys


DEBUG = os.environ.get("DEBUG", "0") == "1"


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs, file=sys.stderr)


N = int(input())
*H, = map(int, input().split())

hist = defaultdict(list)

for i in range(N):
    hist[H[i]].append(i)

ans = 1
for h, indexes in hist.items():
    debug(f'{h=}, {indexes=}')
    if len(indexes) == 1:
        debug('  continue')
        continue

    # dp[i][d] := indexes[i] までを利用した公差 d の数列の長さ
    dp = [[1]*(indexes[-1]-indexes[0]+1) for _ in indexes]
    max_len = 1
    for i in range(len(indexes)):
        for j in range(i+1, len(indexes)):
            d = indexes[j]-indexes[i]
            dp[j][d] += dp[i][d]
            max_len = max(max_len, dp[j][d])

    ans = max(ans, max_len)


print(ans)
