from bisect import bisect_left as bl


N, M = map(int, input().split())
*A, = sorted(map(int, input().split()))
S = sum(A)

i = bl(A, S-M)
if 0 <= i < N and A[bl(A, S-M)] == S-M:
    print('Yes')
else:
    print('No')
