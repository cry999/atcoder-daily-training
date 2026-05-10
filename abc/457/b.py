N = int(input())
A = [list(map(int, input().split())) for _ in range(N)]
X, Y = map(int, input().split())

print(A[X - 1][Y])
