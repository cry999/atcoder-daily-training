import heapq


def debug(*values: object, **kwargs):
    # print('DEBUG:', *values, **kwargs)
    pass


H, W, T = map(int, input().split())
A = [input() for _ in range(H)]

sweets = []
sweets_index = {}

s, g = None, None
for i in range(H):
    for j in range(W):
        if A[i][j] == 'S':
            s = (i, j)
        elif A[i][j] == 'G':
            g = (i, j)
        elif A[i][j] == 'o':
            sweets_index[(i, j)] = len(sweets)
            sweets.append((i, j))


def already_eaten_sweets(bit: int, pos: tuple[int]) -> bool:
    i = sweets_index.get(pos)
    return bit & (1 << i) != 0


def eat_sweets(bit: int, pos: tuple[int]) -> int:
    i = sweets_index.get(pos)
    return bit | (1 << i)


queue = [(0, 0, s, 0)]  # (time, -sweets, pos, sweets_bit)
# visited[h][w] = 訪れた時のお菓子の最大値
# これを超えない時は訪れる必要がない
visited = [[-1] * W for _ in range(H)]
visited[s[0]][s[1]] = 0

while queue:
    t, neg_sweets, (h, w), sweets_bit = heapq.heappop(queue)
    if t+1 > T:
        continue
    sweets = -neg_sweets

    for dh, dw in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        nh, nw = h+dh, w+dw
        # 盤外は skip
        if nh < 0 or H <= nh:
            # debug('h is over', nh)
            continue
        if nw < 0 or W <= nw:
            # debug('w is over', nw)
            continue
        # 壁は skip
        if A[nh][nw] == '#':
            # debug('wall', nh, nw)
            continue
        # 食べていないお菓子がある場合
        n_sweets_bit = sweets_bit
        n_sweets = sweets
        if A[nh][nw] == 'o' and not already_eaten_sweets(sweets_bit, (nh, nw)):
            # お菓子を処理
            debug('eat sweets', nh, nw, sweets+1,
                  bin(sweets_bit)[2:].zfill(18))
            n_sweets_bit = eat_sweets(sweets_bit, (nh, nw))
            n_sweets += 1
        if visited[nh][nw] > n_sweets:
            # 以前に訪れた時よりお菓子の数が少ないなら探索する意味なし
            # debug('visited', nh, nw, visited[nh][nw], n_sweets)
            continue
        visited[nh][nw] = n_sweets
        heapq.heappush(queue, (t+1, -n_sweets, (nh, nw), n_sweets_bit))

debug(visited)
print(visited[g[0]][g[1]])
