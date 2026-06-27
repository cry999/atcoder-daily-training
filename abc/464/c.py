import sys

input = sys.stdin.readline

N, M = map(int, input().split())
hist = [0] * (N + 1)

type_num = 0
events = []
for _ in range(N):
    a, d, b = map(int, input().split())
    hist[a] += 1
    if hist[a] == 1:
        type_num += 1
    events.append((d, a, -1))
    events.append((d, b, +1))
events.sort()

cur = 0
for d in range(1, M + 1):
    while cur < len(events) and events[cur][0] == d:
        _, a, delta = events[cur]
        hist[a] += delta
        if hist[a] == 0:
            type_num -= 1
        elif hist[a] == 1 and delta == +1:
            type_num += 1
        cur += 1

    print(type_num)
