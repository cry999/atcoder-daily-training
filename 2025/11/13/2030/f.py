from bisect import bisect_left
MOD = 10**8

N = int(input())
*A, = map(int, input().split())
A.sort()

S = 0
for i, a in enumerate(A):
    S += a * (N-1)
    j = bisect_left(A, MOD-a, lo=i+1)
    # print(i, a, j, MOD-a, N-j)
    if j >= N:
        continue
    if A[j]+a >= MOD:
        # print(f'{N-j=}')
        S -= (N-j)*MOD
    else:
        # print('N-j-1')
        S -= (N-j-1) * MOD


print(S)
