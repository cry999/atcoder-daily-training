N, K, X = map(int, input().split())
*A, = map(int, input().split())

for i, a in enumerate(A):
    if a >= X:
        k = min(a // X, K)
        K -= k
        A[i] = a - k*X

A.sort(reverse=True)
total = 0
for a in A:
    if K > 0:
        total += max(0, a-X)
        K -= 1
    else:
        total += a
print(total)
