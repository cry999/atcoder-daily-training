H, W, N = map(int, input().split())

X = [[0] * (W+2) for _ in range(H+2)]

for _ in range(N):
    A, B, C, D = map(int, input().split())
    X[A][B] += 1
    X[A][D+1] -= 1
    X[C+1][B] -= 1
    X[C+1][D+1] += 1

# まずは横
for i in range(1, H+1):
    for j in range(1, W+1):
        X[i][j] += X[i][j-1]

# 次に縦
for j in range(1, W+1):
    for i in range(1, H+1):
        X[i][j] += X[i-1][j]

for i in range(1, H+1):
    print(*X[i][1:W+1])
