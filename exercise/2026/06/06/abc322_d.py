P1 = [list(input()) for _ in range(4)]
P2 = [list(input()) for _ in range(4)]
P3 = [list(input()) for _ in range(4)]

S1 = sum(r.count("#") for r in P1)
S2 = sum(r.count("#") for r in P2)
S3 = sum(r.count("#") for r in P3)

if S1 + S2 + S3 != 16:
    print("No")
    exit()

N = 4


def print_P(P: list[list[str]]):
    for r in P:
        print("".join(r))


def rotate(P: list[list[str]], n: int = 1):
    n %= 4
    if n > 1:
        P = rotate(P, n - 1)
    return [[P[j][N - 1 - i] for j in range(N)] for i in range(N)]


def align_lu(P: list[list[str]]):
    R = [["."] * N for _ in range(N)]

    # 上に合わせる
    for i in range(N):
        if P[i].count("#") == 0:
            continue
        for j in range(N - i):
            R[j] = P[j + i][:]
        break

    # 左に合わせる
    for j in range(N):
        for i in range(N):
            if R[i][j] == "#":
                break
        else:
            continue
        if j == 0:
            # 移動する必要なし
            break
        for k in range(N):
            for i in range(N):
                if j + k < N:
                    R[i][k] = R[i][j + k]
                else:
                    R[i][k] = "."
        break

    return R


def place(board: list[list[str]], P: list[list[str]], x: int, y: int):
    for i in range(N):
        for j in range(N):
            if (
                x + i < N
                and y + j < N
                and P[i][j] == "#"
                and board[x + i][y + j] == "#"
            ):
                return False
    for i in range(N):
        for j in range(N):
            if P[i][j] == "#" and x + i < N and y + j < N:
                board[x + i][y + j] = P[i][j]

    return True


def remove(board: list[list[str]], P: list[list[str]], x: int, y: int):
    for i in range(N):
        for j in range(N):
            if (
                x + i < N
                and y + j < N
                and P[i][j] == "#"
                and board[x + i][y + j] == "."
            ):
                return False
    for i in range(N):
        for j in range(N):
            if P[i][j] == "#" and x + i < N and y + j < N:
                board[x + i][y + j] = "."

    return True


# まずは P1 を左上に合わせる
P1 = align_lu(P1)
R2 = [
    align_lu(P2),
    align_lu(rotate(P2)),
    align_lu(rotate(P2, 2)),
    align_lu(rotate(P2, 3)),
]
R3 = [
    align_lu(P3),
    align_lu(rotate(P3)),
    align_lu(rotate(P3, 2)),
    align_lu(rotate(P3, 3)),
]

# P1 は回転せずに位置を決める。
# その後に回転しながら P2, P3 をはめていく。
board = [["."] * N for _ in range(N)]
for pos1 in range(N * N):
    i1, j1 = divmod(pos1, N)
    place(board, P1, i1, j1)

    for p2 in R2:
        for pos2 in range(N * N):
            i2, j2 = divmod(pos2, N)
            if not place(board, p2, i2, j2):
                continue

            for p3 in R3:
                for pos3 in range(N * N):
                    i3, j3 = divmod(pos3, N)
                    if not place(board, p3, i3, j3):
                        continue
                    if any(board[k // N][k % N] == "." for k in range(N * N)):
                        remove(board, p3, i3, j3)
                        continue
                    print("Yes")
                    exit()

            remove(board, p2, i2, j2)

    remove(board, P1, i1, j1)

print("No")
