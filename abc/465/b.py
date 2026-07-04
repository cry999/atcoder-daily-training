X, Y, L, R, A, B = map(int, input().split())
print(sum(X if L <= t < R else Y for t in range(A, B)))
