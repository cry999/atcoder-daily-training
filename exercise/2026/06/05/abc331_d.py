N, Q = map(int, input().split())
P = [input() for _ in range(N)]
ALL_BLACKS = sum(row.count("B") for row in P)

CP = [[0] * (N + 1) for _ in range(N + 1)]
for i in range(N):
    for j in range(N):
        CP[i + 1][j + 1] = int(P[i][j] == "B")

for i in range(N + 1):
    for j in range(N):
        CP[i][j + 1] += CP[i][j]

for i in range(N):
    for j in range(N + 1):
        CP[i + 1][j] += CP[i][j]


def _count_black(i: int, j: int):
    if i < 0 or j < 0:
        return 0
    qx, rx = divmod(i + 1, N)
    qy, ry = divmod(j + 1, N)

    res = qx * qy * ALL_BLACKS

    res += CP[rx][N] * qy
    res += CP[N][ry] * qx
    res += CP[rx][ry]

    return res


def count_black(a: int, b: int, c: int, d: int):
    return (
        _count_black(c, d)
        - _count_black(c, b - 1)
        - _count_black(a - 1, d)
        + _count_black(a - 1, b - 1)
    )


for _ in range(Q):
    a, b, c, d = map(int, input().split())
    print(count_black(a, b, c, d))
