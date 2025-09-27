import bisect

N, K = map(int, input().split())
A = sorted(list(map(int, input().split())))

for i in range(K):
    index = bisect.bisect_left(A, i)
    if index < N and A[index] == i:
        continue
    print(i)
    break
else:
    print(K)
