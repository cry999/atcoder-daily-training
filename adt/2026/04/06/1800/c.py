N, M = map(int, input().split())
S = [input() for _ in range(N)]
T = [input() for _ in range(M)]


def equal(a: int, b: int) -> bool:
    for i in range(M):
        for j in range(M):
            if S[a + i][b + j] != T[i][j]:
                return False
    return True


for a in range(N - M + 1):
    for b in range(N - M + 1):
        if equal(a, b):
            print(a + 1, b + 1)
            break
    else:
        continue
    break
