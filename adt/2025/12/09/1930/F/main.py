N, M = map(int, input().split())
*A, = map(int, input().split())

ai = 0
for i in range(N):
    print(A[ai]-i-1)
    ai += A[ai] == i+1
