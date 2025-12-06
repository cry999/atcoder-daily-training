N, K = map(int, input().split())
*A, = map(int, input().split())

A.sort()

print(min(A[i+N-K-1]-A[i] for i in range(K+1)))
