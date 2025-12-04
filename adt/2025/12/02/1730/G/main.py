import heapq

H, W = map(int, input().split())
S = [[c for c in input()] for _ in range(H)]

queue = []
for i in range(H):
    for j in range(W):
        if S[i][j] == '.':
            S[i][j] = float('inf')
            continue
        S[i][j] = 1
        heapq.heappush(queue, (1, i, j))


def only_one_black(i: int, j: int, depth: int) -> bool:
    black_count = 0
    if i < 0 or H <= i or j < 0 or W <= j:
        return False
    if i > 0 and S[i-1][j] < depth:
        black_count += 1
    if i < H-1 and S[i+1][j] < depth:
        black_count += 1
    if j > 0 and S[i][j-1] < depth:
        black_count += 1
    if j < W-1 and S[i][j+1] < depth:
        black_count += 1
    return black_count == 1


def is_white(i: int, j: int) -> bool:
    return 0 <= i < H and 0 <= j < W and S[i][j] == float('inf')


def debug_print():
    for row in S:
        print(*['#' if x != float('inf') else '.' for x in row])


while queue:
    depth, i, j = heapq.heappop(queue)
    # print(depth, i, j)

    for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        ni, nj = i+di, j+dj
        if is_white(ni, nj) and only_one_black(ni, nj, depth+1):
            S[ni][nj] = depth+1
            heapq.heappush(queue, (depth+1, ni, nj))
        else:
            # debug_print()
            # print('  skip', ni, nj, is_white(i, j),
            #       only_one_black(ni, nj, depth+1))
            pass


print(sum(S[i][j] < float('inf') for i in range(H) for j in range(W)))
# debug_print()
