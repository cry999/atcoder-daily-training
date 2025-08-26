from collections import deque

H, W = map(int, input().split())
grid = []
for _ in range(H):
    grid.append(list(input().strip()))


sx, sy = None, None
gx, gy = None, None

for i in range(H):
    for j in range(W):
        if grid[i][j] == 'S':
            sx, sy = i, j
        elif grid[i][j] == 'G':
            gx, gy = i, j

queue = deque()
queue.append((sx, sy, 0))

# dp[door_state][x][y] = minimum steps to reach (x, y) with door_state
dp = [
    [[float('inf')] * W for _ in range(H)]
    for _ in range(2)
]
dp[0][sx][sy] = 0

# 下、右、上、左
directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]


def can_move(x, y, door_state):
    if not (0 <= x < H and 0 <= y < W):
        return False

    cell = grid[x][y]
    if cell == '#':
        return False
    if cell == 'x' and door_state == 0:
        return False
    if cell == 'o' and door_state == 1:
        return False
    return True


while queue:
    x, y, door = queue.popleft()

    # print('now at (', x, y, ')', '[ switch:', door, ' ]')
    # print(' dp:', dp)

    for dx, dy in directions:
        nx, ny = x + dx, y + dy

        # print(' -> try to (', nx, ny, ')')

        if not can_move(nx, ny, door):
            # print('    cannot move')
            continue

        n_door = 1 - door if grid[nx][ny] == '?' else door
        # print('    can move, next switch:', n_door)

        if dp[n_door][nx][ny] <= dp[door][x][y] + 1:
            continue

        # print('    move to (', nx, ny, ')')
        queue.append((nx, ny, n_door))
        dp[n_door][nx][ny] = dp[door][x][y] + 1

# print(dp)
ans = min(dp[0][gx][gy], dp[1][gx][gy])
if ans != float('inf'):
    print(ans)
else:
    print(-1)
