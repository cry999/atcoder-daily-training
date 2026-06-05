from bisect import bisect_left

N, Q = map(int, input().split())
(*R,) = map(int, input().split())
R.sort()
C = [0] * (N + 1)

for i in range(N):
    C[i + 1] = C[i] + R[i]

for _ in range(Q):
    X = int(input())
    i = bisect_left(C, X)

    if i < N + 1 and C[i] == X:
        i += 1

    print(i - 1)
