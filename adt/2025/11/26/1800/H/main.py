import os
import sys


DEBUG = os.getenv('DEBUG', '0') == '1'


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs, file=sys.stderr)


N, Q = map(int, input().split())
*x, = map(int, input().split())

A = [0] * (N+1)

m = [-1] * (N+1)
cum = [0] * (Q+1)
s = 0
for i in range(Q):
    debug(f'=== Q {i} ===')
    if m[x[i]] == -1:
        m[x[i]] = i
        s += 1
    else:
        # S に追加済みなら除外する。
        s -= 1

        # このタイミングで A[x[i]] の値が確定。
        prev = m[x[i]]
        m[x[i]] = -1

        A[x[i]] += cum[i] - cum[prev]

    cum[i+1] = cum[i] + s
    # debug(f'  {m=}')
    # debug(f'  {cum=}')
    # debug(f'  {A=}')

# debug(f'{m=}')
# debug(f'{cum=}')
for i in range(N+1):
    if m[i] == -1:
        continue
    # debug(f'finalizing A[{i}]: adding {cum[Q]} - {cum[m[i]]}')
    A[i] += cum[Q] - cum[m[i]]

print(*A[1:])
