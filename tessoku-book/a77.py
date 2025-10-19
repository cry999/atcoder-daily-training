N, L = map(int, input().split())
K = int(input())
# 0 からの距離
*A, = map(int, input().split())
# 区間長
B = [
    A[i] if i == 0
    else L-A[i-1] if i == N
    else A[i]-A[i-1]
    for i in range(N+1)
]


def check(x: int) -> bool:
    count, last = 0, 0
    for i in range(N):
        if A[i] - last >= x and L - A[i] >= x:
            count += 1
            last = A[i]
    return count >= K


lo, hi = 0, L // (K+1)
while lo < hi:
    # print('lo:', lo, 'hi:', hi)
    mi = (lo+hi+1)//2
    k, s, min_s = 0, 0, float('inf')
    if check(mi):
        lo = mi
    else:
        hi = mi-1

print(lo)
