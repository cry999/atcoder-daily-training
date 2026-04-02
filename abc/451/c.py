from heapq import heappush, heappop

Q = int(input())

ans = 0
queue = []
for _ in range(Q):
    q, h = map(int, input().split())
    if q == 1:
        ans += 1
        heappush(queue, h)
    else:  # q == 2
        n = 0
        while queue and queue[0] <= h:
            heappop(queue)
            n += 1
        ans -= n
    print(ans)
