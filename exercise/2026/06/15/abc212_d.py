from sortedcontainers import SortedList

Q = int(input())
bag = SortedList()
offset = 0

for _ in range(Q):
    q, *args = map(int, input().split())

    if q == 1:
        x = args[0]
        bag.add(x - offset)
    elif q == 2:
        x = args[0]
        offset += x
    else:
        x = bag.pop(0)
        print(offset + x)
