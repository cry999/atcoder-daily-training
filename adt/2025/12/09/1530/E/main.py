import bisect


N, Q = map(int, input().split())
*A, = sorted(map(int, input().split()))

for _ in range(Q):
    x = int(input())
    print(N-bisect.bisect_left(A, x))
