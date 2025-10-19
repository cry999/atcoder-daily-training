import heapq


N, M = map(int, input().split())
*A, = input().split()
operations = [tuple(map(int, input().split())) for _ in range(M)]

dist = [float('inf')] * (1 << N)


def operate(u: int, op: tuple[int]) -> int:
    x, y, z = op
    return u ^ (1 << (x-1)) ^ (1 << (y-1)) ^ (1 << (z-1))


start = int(''.join(A[::-1]), 2)
queue = [(0, start)]
dist[start] = 0
goal = (1 << N) - 1

while queue:
    d, cursor = heapq.heappop(queue)
    for op in operations:
        next = operate(cursor, op)
        if next == goal:
            print(min(dist[goal], d+1))
            break
        if dist[next] <= d+1:
            continue
        dist[next] = d+1
        heapq.heappush(queue, (d+1, next))
    else:
        # まだ探す
        continue
    # 答えは見つかった
    break
else:
    print(-1)
