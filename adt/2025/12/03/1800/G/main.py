import heapq


N, W = map(int, input().split())

# grid[x] = (y, i)
grid = [[] for _ in range(N)]
for i in range(N):
    x, y = map(int, input().split())
    heapq.heappush(grid[x-1], (y, i))

# 下から何段目か
level, vanish_time = 0, 0
# vanish_time[d] = 下から d 段目の箱の消える時間
vanish_times = []
# levels[i] = 箱 i が下から何段目か
levels = [-1] * N
# grid が空になるまで続ける
while True:
    tmp_vanish_time = 0
    all_empty = True
    for x in range(W):
        # print(f'[{level=}] {x=}')
        if not grid[x]:
            tmp_vanish_time = float('inf')
            # print('  empty')
            continue
        all_empty = False
        y, i = heapq.heappop(grid[x])
        # print(f'  pop (y, i)=({y}, {i})')
        levels[i] = level
        tmp_vanish_time = max(tmp_vanish_time, y)

    if all_empty:
        break

    vanish_time = max(tmp_vanish_time, vanish_time+1)
    vanish_times.append(vanish_time)
    level += 1

# print('vanish_times:', *vanish_times)
# print('levels:', *levels)

Q = int(input())
for _ in range(Q):
    t, i = map(int, input().split())
    if vanish_times[levels[i-1]] > t:
        print('Yes')
    else:
        print('No')
