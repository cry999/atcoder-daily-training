H, W = map(int, input().split())
S = [input() for _ in range(H)]


def s(i: int, j: int, di: int, dj: int) -> str:
    if di > 0 and i + 4 >= H:
        return ""
    if di < 0 and i - 4 < 0:
        return ""
    if dj > 0 and j + 4 >= W:
        return ""
    if dj < 0 and j - 4 < 0:
        return ""

    return "".join(S[i + di * d][j + dj * d] for d in range(5))


DIRS = [
    [0, 1],
    [0, -1],
    [1, 1],
    [1, 0],
    [1, -1],
    [-1, 1],
    [-1, 0],
    [-1, -1],
]
for i in range(H):
    for j in range(W):
        for di, dj in DIRS:
            if s(i, j, di, dj) == "snuke":
                for d in range(5):
                    print(i + 1 + di * d, j + 1 + dj * d)
                exit()
