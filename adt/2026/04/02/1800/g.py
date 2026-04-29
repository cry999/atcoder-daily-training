N = int(input())

A = [[[0] * N for _ in range(N)] for _ in range(N)]

for i in range(N * N):
    (*a,) = map(int, input().split())

    for k in range(N):
        A[i // N][i % N][k] = a[k]

# k 方向に累積和をとる。
for i in range(N):
    for j in range(N):
        for k in range(N - 1):
            A[i][j][k + 1] += A[i][j][k]

# j 方向に累積和をとる
for i in range(N):
    for k in range(N):
        for j in range(N - 1):
            A[i][j + 1][k] += A[i][j][k]

# i 方向に累積和を取る
for j in range(N):
    for k in range(N):
        for i in range(N - 1):
            A[i + 1][j][k] += A[i][j][k]


Q = int(input())
for _ in range(Q):
    lx, rx, ly, ry, lz, rz = map(lambda x: int(x) - 1, input().split())

    ans = A[rx][ry][rz]
    if lx > 0:
        ans -= A[lx - 1][ry][rz]
    if ly > 0:
        ans -= A[rx][ly - 1][rz]
    if lx > 0 and ly > 0:
        ans += A[lx - 1][ly - 1][rz]
    if lz > 0:
        ans -= A[rx][ry][lz - 1]
        if lx > 0:
            ans += A[lx - 1][ry][lz - 1]
        if ly > 0:
            ans += A[rx][ly - 1][lz - 1]
        if lx > 0 and ly > 0:
            ans -= A[lx - 1][ly - 1][lz - 1]
    print(ans)
