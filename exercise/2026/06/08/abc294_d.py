from collections import deque
from sortedcontainers import SortedList

N, Q = map(int, input().split())

waiting = deque(range(1, N + 1))
called = SortedList()

for _ in range(Q):
    # print(f"[DEBUG] {waiting=}, {called=}")
    q, *args = map(int, input().split())

    if q == 1:
        x = waiting.popleft()
        called.add(x)
    elif q == 2:
        x = args[0]
        called.remove(x)
    else:  # q == 3
        print(called[0])
