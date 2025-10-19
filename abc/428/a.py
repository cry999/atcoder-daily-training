S, A, B, X = map(int, input().split())
N = X // (A+B)
print(S*A*N + S*min(X-(A+B)*N, A))
