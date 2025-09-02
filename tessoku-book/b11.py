import bisect

N = int(input())
A = list(sorted(map(int, input().split())))

Q = int(input())
for _ in range(Q):
    X = int(input())
    i = bisect.bisect_right(A, X-1)
    print(i)
