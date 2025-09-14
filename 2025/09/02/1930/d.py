N = int(input())
S = [input() for _ in range(N)]
T = [input() for _ in range(N)]


def rotate_90(M: list[str]) -> list[str]:
    N = len(M)
    return [''.join(M[N-1-j][i] for j in range(N)) for i in range(N)]


def rotate(M: list[str], n: int) -> list[str]:
    for i in range(n):
        M = rotate_90(M)
    return M


def operation(M: list[str], T: list[str]) -> int:
    return sum(
        sum(M[i][j] != T[i][j] for j in range(N)) for i in range(N)
    )


print(min(operation(rotate(S, i), T) + i for i in range(4)))
