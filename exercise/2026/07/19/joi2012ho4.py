N, M = map(int, input().split())

X = N + 3
triangle = [[0] * (X) for _ in range(X)]
for _ in range(M):
    a, b, x = map(int, input().split())
    triangle[a][b] += 1
    triangle[a][b + 1] -= 1
    triangle[a + x + 1][b] -= 1
    triangle[a + x + 1][b + x + 2] += 1
    triangle[a + x + 2][b + 1] += 1
    triangle[a + x + 2][b + x + 2] -= 1

# 横に累積和
for i in range(X):
    for j in range(X - 1):
        triangle[i][j + 1] += triangle[i][j]

# 縦に累積和
for i in range(X - 1):
    for j in range(X):
        triangle[i + 1][j] += triangle[i][j]

# 斜めに累積和
for i in range(X - 1):
    for j in range(X - 1):
        triangle[i + 1][j + 1] += triangle[i][j]

print(sum(sum(c > 0 for c in r) for r in triangle))
