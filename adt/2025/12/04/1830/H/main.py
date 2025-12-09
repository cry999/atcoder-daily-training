from fractions import Fraction
import heapq


N = int(input())

foos = []


def sin(x: int, y: int) -> float:
    return y**2 / (x**2 + y**2)


queue = []
for _ in range(N):
    x, y = map(int, input().split())

    heapq.heappush(queue, (
        Fraction(y, x-1) if x > 1 else float('inf'),
        Fraction(y-1, x),
    ))

cur_tan = 0
cnt = 0
# print(queue)
while queue:
    max_tan, min_tan = heapq.heappop(queue)
    if min_tan >= cur_tan:
        cur_tan = max_tan
        cnt += 1

print(cnt)
