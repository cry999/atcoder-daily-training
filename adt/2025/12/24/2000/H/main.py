import heapq


T = int(input())

for _ in range(T):
    N = int(input())
    A = [int(input()) for _ in range(2 * N)]

    queue = [-A[0]]
    score = 0
    for i in range(1, N):
        score -= heapq.heappop(queue)
        heapq.heappush(queue, -A[2 * i - 1])
        heapq.heappush(queue, -A[2 * i])
    print(score - heapq.heappop(queue))
