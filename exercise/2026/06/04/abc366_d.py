N = int(input())
A = [[[] for _ in range(N)] for _ in range(N)]

for x in range(N):
    for y in range(N):
        A[x][y] = list(map(int, input().split()))

C = [[[0] * (N + 1) for _ in range(N + 1)] for _ in range(N + 1)]

for x in range(N):
    for y in range(N):
        for z in range(N):
            C[x + 1][y + 1][z + 1] = A[x][y][z]

for x in range(N + 1):
    for y in range(N + 1):
        for z in range(N):
            C[x][y][z + 1] += C[x][y][z]

for x in range(N + 1):
    for y in range(N):
        for z in range(N + 1):
            C[x][y + 1][z] += C[x][y][z]

for x in range(N):
    for y in range(N + 1):
        for z in range(N + 1):
            C[x + 1][y][z] += C[x][y][z]

Q = int(input())
for _ in range(Q):
    lx, rx, ly, ry, lz, rz = map(int, input().split())

    ans = C[rx][ry][rz]
    ans -= C[lx - 1][ry][rz]
    ans -= C[rx][ly - 1][rz]
    ans -= C[rx][ry][lz - 1]
    ans += C[rx][ly - 1][lz - 1]
    ans += C[lx - 1][ry][lz - 1]
    ans += C[lx - 1][ly - 1][rz]
    ans -= C[lx - 1][ly - 1][lz - 1]

    print(ans)
