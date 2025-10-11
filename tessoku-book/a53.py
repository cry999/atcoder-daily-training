import heapq

Q = int(input())
queue = []

for _ in range(Q):
    query = list(map(int, input().split()))
    if query[0] == 1:
        price = query[1]
        heapq.heappush(queue, price)
    elif query[0] == 2:
        print(queue[0])
    else:
        heapq.heappop(queue)
