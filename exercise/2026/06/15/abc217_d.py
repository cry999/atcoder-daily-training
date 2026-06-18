from sortedcontainers import SortedList
import sys

input = sys.stdin.readline

L, Q = map(int, input().split())

cut = SortedList([0, L])

for _ in range(Q):
    c, x = map(int, input().split())

    if c == 1:
        cut.add(x)
    else:
        i = cut.bisect_left(x)
        print(cut[i] - cut[i - 1])
