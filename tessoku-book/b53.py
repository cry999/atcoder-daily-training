# b39
import heapq

N, D = map(int, input().split())

not_yet = []
ready = []

for _ in range(N):
    X, Y = map(int, input().split())
    heapq.heappush(not_yet, (X, Y))

total = 0
for d in range(1, D+1):
    while not_yet:
        X, Y = heapq.heappop(not_yet)
        if X > d:
            heapq.heappush(not_yet, (X, Y))
            break
        heapq.heappush(ready, -Y)
    if ready:
        Y = -heapq.heappop(ready)
        total += Y

print(total)
