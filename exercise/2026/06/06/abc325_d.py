from sortedcontainers import SortedList
from collections import deque

N = int(input())

entry_queue = deque(sorted(tuple(map(int, input().split())) for _ in range(N)))
print_queue = SortedList()

t = 1
ans = 0
while entry_queue or print_queue:
    while entry_queue and entry_queue[0][0] <= t:
        time, duration = entry_queue.popleft()
        print_queue.add(time + duration)

    while print_queue and print_queue[0] < t:
        print_queue.pop(0)

    if print_queue:
        print_queue.pop(0)
        ans += 1

    if print_queue:
        t += 1
    elif entry_queue:
        t = max(t, entry_queue[0][0])

print(ans)
