SHIFT = 10**9

A, B, C, D = map(lambda x: int(x) + SHIFT, input().split())

qx, rx = divmod(C - A, 4)
qy, ry = divmod(D - B, 2)

BLACKS = [
    [2, 1, 0, 1],
    [1, 2, 1, 0],
]


def calc(x: int, y: int):
    qx, rx = divmod(x, 4)
    qy, ry = divmod(y, 2)

    # 8: sum(BLACKS)
    s = 8 * qx * qy

    for xx in range(rx):
        s += (BLACKS[0][xx] + BLACKS[1][xx]) * qy
    for yy in range(ry):
        # 4: sum(BLACKS[0 or 1])
        s += 4 * qx
    for xx in range(rx):
        for yy in range(ry):
            s += BLACKS[yy][xx]

    return s


print(calc(C, D) - calc(C, B) - calc(A, D) + calc(A, B))
