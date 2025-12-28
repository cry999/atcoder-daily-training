from sortedcontainers import SortedSet, SortedList
from collections import defaultdict


N = int(input())
Q = int(input())

boxes = defaultdict(SortedList)
card_to_boxes = defaultdict(SortedSet)

for _ in range(Q):
    *query, = map(int, input().split())
    if query[0] == 1:
        _, i, j = query
        boxes[j].add(i)
        card_to_boxes[i].add(j)
    elif query[0] == 2:
        _, i = query
        print(*boxes[i])
    else:  # query[0] == 3
        _, i = query
        print(*card_to_boxes[i])
