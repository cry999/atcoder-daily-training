from math import sqrt

N = int(input())
now = (0, 0)
cost = 0
for _ in range(N):
    x, y = map(int, input().split())
    cost += sqrt((x - now[0]) ** 2 + (y - now[1]) ** 2)
    now = (x, y)

cost += sqrt(now[0] ** 2 + now[1] ** 2)
print(cost)
