import heapq


H, W = map(int, input().split())
S = [input() for _ in range(H)]
C = [[float('inf')] * W for _ in range(H)]

queue = []


def count_adjacent(h: int, w: int, c: int) -> int:
    return sum(
        0 <= nh < H and 0 <= nw < W and C[nh][nw] < c
        for (nh, nw) in [(h-1, w), (h+1, w), (h, w-1), (h, w+1)]
    )


def print_C():
    for row in C:
        print(*[c if c < float('inf') else '-' for c in row])
    print('---')


count = 0
for h in range(H):
    for w in range(W):
        if S[h][w] == '.':
            continue
        C[h][w] = 0
        count += 1
        if h > 0 and S[h-1][w] != '#':
            heapq.heappush(queue, (1, h-1, w))
        if h < H-1 and S[h+1][w] != '#':
            heapq.heappush(queue, (1, h+1, w))
        if w > 0 and S[h][w-1] != '#':
            heapq.heappush(queue, (1, h, w-1))
        if w < W-1 and S[h][w+1] != '#':
            heapq.heappush(queue, (1, h, w+1))
# print(f'{queue=}')
while queue:
    turn, h, w = heapq.heappop(queue)
    if C[h][w] <= turn:
        # print(f'skip {turn} {h} {w}')
        continue
    if count_adjacent(h, w, turn) != 1:
        # print(f'skip {turn} {h} {w} not an adjacent')
        continue
    # print(f'pop {turn} {h} {w}')
    C[h][w] = turn
    count += 1
    # print_C()
    if h > 0 and C[h-1][w] == float('inf') and S[h-1][w] != '#':
        heapq.heappush(queue, (turn+1, h-1, w))
    if h < H-1 and C[h+1][w] == float('inf') and S[h+1][w] != '#':
        heapq.heappush(queue, (turn+1, h+1, w))
    if w > 0 and C[h][w-1] == float('inf') and S[h][w-1] != '#':
        heapq.heappush(queue, (turn+1, h, w-1))
    if w < W-1 and C[h][w+1] == float('inf') and S[h][w+1] != '#':
        heapq.heappush(queue, (turn+1, h, w+1))

print(count)
