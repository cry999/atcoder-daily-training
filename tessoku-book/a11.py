N, X = map(int, input().split())
A = list(map(int, input().split()))

l, r = 0, N-1
while l <= r:
    m = (l + r) // 2
    if A[m] > X:
        r = m-1
    elif A[m] < X:
        l = m+1
    else:
        print(m + 1)
        exit()
print(-1)
