N = int(input())

X = [[0] * (1501) for _ in range(1501)]

for _ in range(N):
    A, B, C, D = map(int, input().split())
    X[A][B] += 1
    X[A][D] -= 1
    X[C][B] -= 1
    X[C][D] += 1

for i in range(1501):
    for j in range(1, 1501):
        X[i][j] += X[i][j-1]

for j in range(1501):
    for i in range(1, 1501):
        X[i][j] += X[i-1][j]

# 10x10 を print で表示
# for i in range(1, 11):
#     print(*X[i][1:11])

print(sum(sum(1 for v in row if v > 0) for row in X))
