from collections import deque

H, W = map(int, input().split())
grid = []
for _ in range(H):
    grid.append(list(input().strip()))


start_row, start_col = None, None
goal_row, goal_col = None, None

for i in range(H):
    for j in range(W):
        if grid[i][j] == 'S':
            start_row, start_col = i, j
        elif grid[i][j] == 'G':
            goal_row, goal_col = i, j

queue = deque([(start_row, start_col, 0, 0)])
visited = set()
visited.add((start_row, start_col, 0))

directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

while queue:
    row, col, door_state, steps = queue.popleft()

    if row == goal_row and col == goal_col:
        print(steps)
        exit()

    for dr, dc in directions:
        new_row, new_col = row + dr, col + dc

        if 0 <= new_row < H and 0 <= new_col < W:
            cell = grid[new_row][new_col]

            if cell == '#':
                continue

            new_door_state = door_state

            if cell == 'x' and door_state == 0:
                continue
            elif cell == 'o' and door_state == 1:
                continue
            elif cell == '?':
                new_door_state = 1 - door_state

            state = (new_row, new_col, new_door_state)
            if state not in visited:
                visited.add(state)
                queue.append((new_row, new_col, new_door_state, steps + 1))

print(-1)
