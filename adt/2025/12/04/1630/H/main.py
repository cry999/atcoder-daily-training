from collections import deque
import heapq
import os


DEBUG = os.getenv('DEBUG', '0') == '1'


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


Q = int(input())

temp_list = deque()
sorted_list = []

for _ in range(Q):
    *query, = map(int, input().split())
    if query[0] == 1:
        temp_list.append(query[1])
    if query[0] == 2:
        if sorted_list:
            print(heapq.heappop(sorted_list))
        else:
            print(temp_list.popleft())
    if query[0] == 3:
        while temp_list:
            heapq.heappush(sorted_list, temp_list.popleft())
