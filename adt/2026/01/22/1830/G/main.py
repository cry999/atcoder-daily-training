from sortedcontainers import SortedList

Q = int(input())
queue = SortedList()
for _ in range(Q):
    q, *args = map(int, input().split())

    if q == 1:
        queue.add(args[0])
    elif q == 2:
        x, k = args
        i = queue.bisect_right(x) - 1
        if i + 1 < k:
            print(-1)
        else:
            print(queue[i - k + 1])
    else:  # q == 3
        x, k = args
        i = queue.bisect_left(x)
        if i + k - 1 >= len(queue):
            print(-1)
        else:
            print(queue[i + k - 1])
