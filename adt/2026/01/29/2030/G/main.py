from bisect import bisect_left as bl

N = int(input())
(*A,) = map(int, input().split())

cum = [0] * (N + 1)

for i in range(N):
    cum[i + 1] = cum[i]
    if i & 1:
        cum[i + 1] += A[i + 1] - A[i]

Q = int(input())
for _ in range(Q):
    ans = 0
    l, r = map(int, input().split())
    li = bl(A, l)
    if li % 2 == 0:
        ans += A[li] - l

    ri = bl(A, r)
    if ri % 2 == 0:
        ans -= A[ri] - r

    ans += cum[ri] - cum[li]
    print(ans)
