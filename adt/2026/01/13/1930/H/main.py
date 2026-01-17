from heapq import heappop as hpop, heappush as hpush
from collections import deque

Q = int(input())

sorted_queue = []
queue = deque()

for _ in range(Q):
    q, *args = map(int, input().split())

    if q == 1:
        queue.append(args[0])
    elif q == 2:
        if sorted_queue:
            print(hpop(sorted_queue))
        else:
            print(queue.popleft())
    else:  # q == 3
        while queue:
            hpush(sorted_queue, queue.popleft())
