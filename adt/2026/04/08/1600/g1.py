from sortedcontainers import SortedList

N, Q = map(int, input().split())

waiting_list = [N - i - 1 for i in range(N)]
called = SortedList()
done = [False] * N

for _ in range(Q):
    e, *args = map(int, input().split())

    if e == 1:
        x = waiting_list.pop()
        called.add(x)
    elif e == 2:
        x = args[0] - 1
        done[x] = True
    else:  # e == 3
        while done[called[0]]:
            called.pop(0)

        x = called[0]
        print(x + 1)
