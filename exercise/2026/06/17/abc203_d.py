N, K = map(int, input().split())
A = [list(map(int, input().split())) for _ in range(N)]

lo, hi = -1, 10**9

C = [[False] * (N + 1) for _ in range(N + 1)]

bound = (K * K + 1) // 2


def check(X: int):
    # X 以下の数が KxK の正方形の中で中央値になるか？
    # -> X 以下の数が KxK の正方形の中で (K^2 + 1) // 2 個以上あるか？

    # とりあえず二次元累積和
    for pos in range(N * N):
        i, j = divmod(pos, N)
        C[i + 1][j + 1] = A[i][j] <= X

    for i in range(N + 1):
        for j in range(N):
            C[i][j + 1] += C[i][j]

    for i in range(N):
        for j in range(N + 1):
            C[i + 1][j] += C[i][j]

    for i in range(N - K + 1):
        for j in range(N - K + 1):
            # (i, j) を左上とする KxK の区間の X 以下の個数は？
            cnt = C[i + K][j + K] - C[i + K][j] - C[i][j + K] + C[i][j]

            if cnt >= bound:
                return True
    return False


while hi - lo > 1:
    X = (lo + hi) // 2

    if check(X):
        hi = X
    else:
        lo = X

print(hi)
