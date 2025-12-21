N = int(input())
*A, = map(int, input().split())

for i in range(N-1):
    A[i+1] += A[i]

ceil = min(min(A), 0)
print(A[-1]-ceil)
