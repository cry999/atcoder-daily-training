import bisect
import sys
import os


DEBUG = os.getenv('DEBUG', '0') == '1'


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs, file=sys.stderr)


N = int(input())
*X, = map(int, input().split())
*P, = map(int, input().split())
Q = int(input())

*XP, = sorted(zip(X, P))

cum = [0] * (N+1)
for i in range(N):
    cum[i+1] = cum[i] + XP[i][1]

for _ in range(Q):
    L, R = map(int, input().split())
    # debug(f'Query: {L=}, {R=}')
    # debug(f'XP: {XP}')
    li = bisect.bisect_left(XP, (L, -1))
    ri = bisect.bisect_left(XP, (R, -1))
    if ri < N and XP[ri][0] == R:
        ri += 1

    # debug(f'{li=}, {ri=}')
    print(cum[ri] - cum[li])
