N, H, W = map(int, input().split())
tiles = [tuple(map(int, input().split())) for _ in range(N)]
tiles.sort(key=lambda x: x[0] * x[1], reverse=True)

board = [0 for _ in range(H)]


def print_board():
    print("-" * W)
    for row in board:
        print(f"{row:0{W}b}")
    print("-" * W)


def init():
    global board
    for h in range(H):
        board[h] = 0


def write(h: int, w: int, a: int, b: int) -> bool:
    global board

    if h + a > H or w + b > W:
        return False

    mask = (1 << b) - 1
    mask <<= w

    for nh in range(h, h + a):
        if board[nh] & mask:
            return False
    for nh in range(h, h + a):
        board[nh] |= mask
    return True


def clear(h: int, w: int, a: int, b: int):
    global board

    if h + a > H or w + b > W:
        return

    mask = (1 << b) - 1
    mask <<= w

    for nh in range(h, h + a):
        board[nh] ^= mask
    return


def dfs(bit: int) -> bool:
    global board

    if bit == 0:
        mask = (1 << W) - 1
        for h in range(H):
            if board[h] != mask:
                return False
        return True

    i = 0
    while not bit & (1 << i):
        i += 1

    bit ^= 1 << i
    a, b = tiles[i]
    mask = (1 << b) - 1

    for h in range(H - a + 1):
        for w in range(W - b + 1):
            if board[h] & (mask << w):
                continue
            if not write(h, w, a, b):
                continue
            if dfs(bit):
                return True
            clear(h, w, a, b)

    if a == b:
        return False

    mask = (1 << a) - 1
    for h in range(H - b + 1):
        for w in range(W - a + 1):
            if board[h] & (mask << w):
                continue
            if not write(h, w, b, a):
                continue
            if dfs(bit):
                return True
            clear(h, w, b, a)
    return False


def sum_area(bit: int) -> int:
    area = 0
    for i in range(N):
        if bit & (1 << i):
            area += tiles[i][0] * tiles[i][1]
    return area


for bit in range(1, 1 << N):
    if sum_area(bit) != H * W:
        continue
    init()

    if dfs(bit):
        print("Yes")
        exit()
print("No")
