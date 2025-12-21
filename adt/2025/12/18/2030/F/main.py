from bisect import bisect_left


N = int(input())
*A, = map(int, input().split())

lo = 0
ans = 0
for i in range(N):
    j = bisect_left(A, 2*A[i], lo=lo)
    if j < N:
        ans += N-j
print(ans)
