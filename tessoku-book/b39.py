import heapq

N, D = map(int, input().split())

cannot_work = []  # まだ着手できない仕事
for d in range(N):
    X, Y = map(int, input().split())
    heapq.heappush(cannot_work, (X, Y))

working = []  # 着手可能な仕事
ans = 0
for d in range(1, D+1):
    while cannot_work:
        X, Y = heapq.heappop(cannot_work)
        if X > d:
            heapq.heappush(cannot_work, (X, Y))
            break
        heapq.heappush(working, -Y)
    if working:
        Y = -heapq.heappop(working)
        ans += Y
print(ans)
