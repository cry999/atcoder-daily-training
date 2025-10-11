from random import randint

N = 100

A = [list(map(int, input().split())) for _ in range(N)]
B = [[0]*N for _ in range(N)]


def score():
    return 200_000_000
    - sum(abs(A[j][i] - B[j][i]) for j in range(N) for i in range(N))


def mt_plus(x: int, y: int, h: int):
    B[y][x] += h
    for dh in range(1, h):
        for dx in range(1, dh+1):
            dy = dh-dx
            if 0 <= x+dx < N and 0 <= y+dy < N:
                B[y+dy][x+dx] += h-dh
            if 0 <= x+dx < N and 0 <= y-dy < N:
                B[y-dy][x+dx] += h-dh
            if 0 <= x-dx < N and 0 <= y+dy < N:
                B[y+dy][x-dx] += h-dh
            if 0 <= x-dx < N and 0 <= y-dy < N:
                B[y-dy][x-dx] += h-dh


Q = 1000
MAX_H = 20
queries = []
for _ in range(Q):
    x, y = randint(0, N-1), randint(0, N-1)
    h = randint(1, max(min(MAX_H, A[y][x]-B[y][x]), 1))
    mt_plus(x, y, h)
    queries.append((x, y, h))

M = 10000
DXY = 1
DH = 14
for _ in range(M):
    q = randint(0, Q-1)
    x, y, h = queries[q]
    s = score()

    mt_plus(x, y, -h)
    dx, dy, dh = randint(-DXY, DXY), randint(-DXY, DXY), randint(-DH, DH)
    nx, ny, nh = x+dx, y+dy, h+dh
    nx, ny, nh = max(min(nx, N-1), 0), max(min(ny, N-1), 0), max(min(nh, N), 1)
    mt_plus(nx, ny, nh)
    ns = score()

    if s < ns:  # 更新
        queries[q] = (nx, ny, nh)
    else:  # 戻す
        mt_plus(nx, ny, -nh)
        mt_plus(x, y, h)

print(Q)
for x, y, h in queries:
    print(x, y, h)
