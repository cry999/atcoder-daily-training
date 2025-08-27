N = int(input())

A = list(map(int, input().split()))

for i in range(N-1):
    S, T = map(int, input().split())
    n = A[i] // S
    A[i] -= S * n
    A[i+1] += T * n

print(A[N-1])
