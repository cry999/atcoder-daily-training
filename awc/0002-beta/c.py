N, M = map(int, input().split())

d = 0

for _ in range(N):
    a, b = map(int, input().split())
    day = (M - a) // b
    if (M - a) % b != 0:
        day += 1

    d = max(d, day)

print(d)
