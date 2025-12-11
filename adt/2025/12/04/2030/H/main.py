import os
import sys


DEBUG = os.getenv('DEBUG', '0') == '1'


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs, file=sys.stderr)


N, D = map(int, input().split())
X, Y = [], []

for _ in range(N):
    x, y = map(int, input().split())
    X.append(x)
    Y.append(y)

X.sort()
Y.sort()

M = max(max(abs(x), abs(y)) for x, y in zip(X, Y))

# right_xi: x > xi を満たす最大の i
right_xi = -1
# right_yi: y > yi を満たす最大の i
right_yi = -1
debug(f'{M=}, {D=}')
fx = N*(M+D+1) + sum(X)
gy = N*(M+D+1) + sum(Y)
F, G = [], []
for x in range(-M-D, M+D+1):
    fx += 2*(right_xi+1)-N
    while right_xi+1 < N and x == X[right_xi+1]:
        right_xi += 1

    F.append(fx)

    gy += 2*(right_yi+1)-N
    while right_yi+1 < N and x == Y[right_yi+1]:
        right_yi += 1
    # debug(f'x={x}, fy={gy}, right_yi={right_yi}')

    G.append(gy)

F.sort()
G.sort()

# debug(f'{F=}')
# debug(f'{G=}')

# G[j] <= D-F[i] を満たす最大の j
j = -1
cnt = 0
for i in range(len(F)):
    fi = F[-(i+1)]
    # debug(f'{fi=}')
    # debug(f'  {G[j+1]=} <= {D-fi=}')
    while j+1 < len(G) and G[j+1] <= D-fi:
        # debug(f'  {G[j+1]=} <= {D-fi=}')
        j += 1

    cnt += j+1
print(cnt)
