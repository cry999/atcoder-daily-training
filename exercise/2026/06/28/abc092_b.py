N = int(input())
D, X = map(int, input().split())
print(X + sum((D - 1) // int(input()) for _ in range(N)) + N)
