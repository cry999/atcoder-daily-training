from sortedcontainers import SortedList

N, M = map(int, input().split())

waiting = SortedList(range(N))
somen = [0] * N
eating = SortedList()

for _ in range(M):
    T, W, S = map(int, input().split())

    while eating and eating[0][0] <= T:
        _, i = eating.pop(0)
        waiting.add(i)

    if waiting:
        i = waiting.pop(0)
        somen[i] += W
        eating.add((T + S, i))

print("\n".join(map(str, somen)))
