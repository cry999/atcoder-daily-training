from sortedcontainers import SortedList

N, Q = map(int, input().split())

not_call = 0
second_call = SortedList()

finished = [False] * N

for _ in range(Q):
    q, *args = map(int, input().split())

    if q == 1:
        second_call.add(not_call)
        not_call += 1
    elif q == 2:
        x = args[0] - 1
        finished[x] = True
    else:
        while finished[second_call[0]]:
            second_call.pop(0)
        print(second_call[0] + 1)
