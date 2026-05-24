import sys

input = sys.stdin.readline

N, Q = map(int, input().split())
(*A,) = map(int, input().split())

# 累積和でいけそう。 O(N)

C = [0] * (N + 1)
for i in range(N):
    C[i + 1] = C[i] + A[i]

for _ in range(Q):
    q, *args = map(int, input().split())

    if q == 1:  # swap
        x = args[0] - 1
        C[x + 1] += A[x + 1] - A[x]
        A[x + 1], A[x] = A[x], A[x + 1]
    else:  # q == 2:  # range sum
        l, r = args
        print(C[r] - C[l - 1])
