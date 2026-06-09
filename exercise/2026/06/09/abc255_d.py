from bisect import bisect_right

N, Q = map(int, input().split())
(*A,) = map(int, input().split())

A.sort()
C = [0] * (N + 1)
for i in range(N):
    C[i + 1] = C[i] + A[i]
# print(A, C)
for _ in range(Q):
    X = int(input())

    i = bisect_right(A, X)
    ans = X * (i) - C[i] + C[N] - C[i] - X * (N - i)
    print(ans)
    # print("[DEBUG]", i, X, C[i])
