A, X, M = map(int, input().split())


def prod_matrix_mod(
    a: list[list[int]],
    b: list[list[int]],
    mod: int,
) -> list[list[int]]:
    c = [[0] * len(a) for _ in range(len(a))]

    for i in range(len(a)):
        for j in range(len(a)):
            for k in range(len(a)):
                c[i][j] += a[i][k]*b[k][j]
                c[i][j] %= mod
    return c


def pow_matrix_mod(a: list[list[int]], exp: int, mod: int) -> list[list[int]]:
    b = [[1 if i == j else 0 for i in range(len(a))] for j in range(len(a))]

    while exp:
        if exp & 1:
            b = prod_matrix_mod(b, a, mod)
        a = prod_matrix_mod(a, a, mod)
        exp >>= 1

    return b


print(pow_matrix_mod([[A, 1], [0, 1]], X, M)[0][1])
