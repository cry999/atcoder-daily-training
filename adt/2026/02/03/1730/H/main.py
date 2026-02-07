from sortedcontainers import SortedList

T = int(input())

for _ in range(T):
    N, K = map(int, input().split())
    (*A,) = map(int, input().split())
    (*B,) = map(int, input().split())
    AB = sorted(zip(A, B))

    queue = SortedList()

    ans = float("inf")
    sum_b = 0
    for a, b in AB:
        i = queue.bisect_right(b)
        if i <= K:
            queue.add(b)
            sum_b += b
        if len(queue) > K:
            sum_b -= queue.pop()
        if len(queue) == K:
            ans = min(ans, a * sum_b)

    print(ans)
