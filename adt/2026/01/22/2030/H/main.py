A, X, M = map(int, input().split())

B = [[A, 1], [0, 1]]
C = [[1, 0], [0, 1]]


def matmul(D: list[list[int]], E: list[list[int]], M: int) -> list[list[int]]:
    F = [[0] * len(E[0]) for _ in range(len(D))]
    for i in range(len(D)):
        for j in range(len(E[0])):
            for k in range(len(E)):
                F[i][j] += D[i][k] * E[k][j]
                F[i][j] %= M
    return F


x = X
while x:
    if x & 1:
        C = matmul(B, C, M)
    B = matmul(B, B, M)
    x >>= 1

print(matmul(C, [[0], [1]], M)[0][0])
