N = int(input())

A = [input() for _ in range(N)]
B = [[""] * N for _ in range(N)]

for i in range(N // 2):
    for j in range(i, N - i):
        if i % 4 == 0:
            B[i][j] = A[N - j - 1][i]
            B[N - i - 1][j] = A[N - j - 1][N - i - 1]
            B[j][i] = A[N - i - 1][j]
            B[j][N - i - 1] = A[i][j]
        elif i % 4 == 1:
            B[i][j] = A[N - i - 1][N - j - 1]
            B[N - i - 1][j] = A[i][N - j - 1]
            B[j][i] = A[N - j - 1][N - i - 1]
            B[j][N - i - 1] = A[N - j - 1][i]
        elif i % 4 == 2:
            B[i][j] = A[j][N - i - 1]
            B[N - i - 1][j] = A[j][i]
            B[j][i] = A[i][N - j - 1]
            B[j][N - i - 1] = A[N - i - 1][N - j - 1]
        else:
            B[i][j] = A[i][j]
            B[N - i - 1][j] = A[N - i - 1][j]
            B[j][i] = A[j][i]
            B[j][N - i - 1] = A[j][N - i - 1]

print("\n".join("".join(row) for row in B))
