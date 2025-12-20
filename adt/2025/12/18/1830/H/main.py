import heapq


T = int(input())

for _ in range(T):
    N, K = map(int, input().split())
    *AB, = zip(map(int, input().split()),  map(int, input().split()))
    AB.sort()

    S = 0
    max_a = 0
    queue = []

    for k in range(K):
        a, b = AB[k]
        max_a = max(max_a, a)
        S += b
        heapq.heappush(queue, -b)

    ans = max_a*S
    for k in range(K, N):
        a, b = AB[k]
        max_b = -heapq.heappop(queue)
        heapq.heappush(queue, -b)
        max_a = a
        S += -max_b + b
        ans = min(ans, max_a*S)

    print(ans)
