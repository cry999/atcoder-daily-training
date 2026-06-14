from math import gcd

N = int(input())
cities = [tuple(map(int, input().split())) for _ in range(N)]

count = {}

for i in range(N):
    x1, y1 = cities[i]
    for j in range(i + 1, N):
        x2, y2 = cities[j]

        g = gcd(abs(x2 - x1), abs(y2 - y1))
        dx, dy = (x2 - x1) // g, (y2 - y1) // g

        count[(dx, dy)] = 1
        count[(-dx, -dy)] = 1

print(sum(count.values()))
