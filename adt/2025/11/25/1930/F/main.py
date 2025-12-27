N, K = map(int, input().split())
*A, = map(int, input().split())

A.sort()

i = 0
mex = 0
for k in range(K):
    if i >= N or A[i] != k:
        break
    mex += 1
    while i < N and A[i] == k:
        i += 1

print(mex)
