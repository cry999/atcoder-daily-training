from bisect import bisect_right

N = int(input())

L = [0] * N
H = [0] * N

for i in range(N):
    h, l = map(int, input().split())
    L[i] = l
    H[i] = h

for i in range(N - 1, 0, -1):
    H[i - 1] = max(H[i], H[i - 1])

Q = int(input())
(*T,) = map(int, input().split())
for t in T:
    i = bisect_right(L, t)
    print(H[i])
