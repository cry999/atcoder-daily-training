N = int(input())
S = [list(input()) for _ in range(N)]
T = [list(input()) for _ in range(N)]


def equal(S: list[list[str]], T: list[list[str]]) -> bool:
    for i in range(N):
        for j in range(N):
            if S[i][j] != T[i][j]:
                return False
    return True


def fit(s: list[list[str]]) -> list[list[str]]:
    b = [["."] * N for _ in range(N)]
    c = [["."] * N for _ in range(N)]
    min_row = N
    min_col = N
    for i in range(N):
        for j in range(N):
            if s[i][j] == "#":
                min_row = min(min_row, i)
                min_col = min(min_col, j)
    for i in range(min_row, N):
        for j in range(N):
            b[i - min_row][j] = s[i][j]
    for i in range(N):
        for j in range(N):
            c[i][j - min_col] = b[i][j]
    return c


def rotate(s: list[list[str]]) -> list[list[str]]:
    b = [[""] * N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            b[i][j] = s[j][N - i - 1]
    return fit(b)


def print_matrix(s: list[list[str]]):
    for row in s:
        print("".join(row))
    return


S = fit(S)
T = fit(T)
for _ in range(4):
    if equal(S, T):
        print("Yes")
        break
    S = rotate(S)
else:
    print("No")
