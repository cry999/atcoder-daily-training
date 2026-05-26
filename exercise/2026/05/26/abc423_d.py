from heapq import heappop, heappush

N, K = map(int, input().split())
restaurants = []
guests_in_restaurant = 0

time = 0
for _ in range(N):
    enter, stay, size = map(int, input().split())

    while guests_in_restaurant + size > K:
        time, leave = heappop(restaurants)
        guests_in_restaurant -= leave

    time = max(time, enter)
    print(time)
    # print(f"  push {time+stay} {size} @{time}")
    heappush(restaurants, (time + stay, size))
    guests_in_restaurant += size
