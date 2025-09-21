X, K = map(int, input().split())

for i in range(1, K+1):
    Y = (X % pow(10, i)) // pow(10, i-1)
    X = X - Y * pow(10, i-1)
    if Y > 4:
        X += pow(10, i)
    # print(i, Y, X)

print(X)
