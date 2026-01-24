N, M = map(int, input().split())
(*X,) = map(int, input().split())
(*A,) = map(int, input().split())

if N != sum(A):
    print(-1)
    exit()

XA = sorted(zip(X, A))

i = 0
x0, a0 = XA[i]
i += 1
ans = 0
while i < M:
    x1, a1 = XA[i]
    if x1 - x0 > a0:
        print(-1)
        exit()
    ans += (a0 * (a0 - 1) // 2) - ((a0 - (x1 - x0)) * (a0 - (x1 - x0) - 1) // 2)
    x0, a0 = x1, a0 - (x1 - x0) + a1
    i += 1

if N - x0 == a0 - 1:
    x1 = N
    ans += (a0 * (a0 - 1) // 2) - ((a0 - (x1 - x0)) * (a0 - (x1 - x0) - 1) // 2)
    print(ans)
else:
    print(-1)
