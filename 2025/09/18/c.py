import bisect

N = int(input())
P = list(map(int, input().split()))
sorted_p = sorted(P)

for p in P:
    index = bisect.bisect_right(sorted_p, p)
    print(N-index+1)
