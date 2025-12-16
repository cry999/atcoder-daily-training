import os
import sys


DEBUG = os.getenv('DEBUG', '0') == '1'


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs, file=sys.stderr)


N, A, B = map(int, input().split())
*D, = map(int, input().split())

*E, = sorted(set(d % (A+B) for d in D))
# debug(f'{E=}')
# E の数字の間隔で B をすっぽり含めるものがあれば予定は全部休日の可能性あり
max_interval = E[0] + (A+B-E[-1]-1)
for i in range(len(E)-1):
    max_interval = max(max_interval, E[i+1]-E[i]-1)

debug(f'{max_interval=}, {B=}')
if B <= max_interval:
    print('Yes')
else:
    print('No')
