N, K, X = map(int, input().split())
(*A,) = map(int, input().split())

A.sort(reverse=True)

sake = 0
for k in range(K):
    sake += A[N - K + k]
    if sake >= X:
        print(N - K + k + 1)
        break
else:
    print(-1)
