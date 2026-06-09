N = int(input())
ZERO = 1000
# ZERO = 10
is_black = [[False] * (2 * ZERO + 1) for _ in range(2 * ZERO + 1)]
visited = [[-1] * (2 * ZERO + 1) for _ in range(2 * ZERO + 1)]

q = []

for i in range(N):
    x, y = map(int, input().split())
    is_black[x + ZERO][y + ZERO] = True

    q.append((x, y, i))

DIRS = [
    (-1, -1),
    (-1, 0),
    (0, -1),
    (0, +1),
    (+1, 0),
    (+1, +1),
]

while q:
    x, y, id = q.pop()
    # print("[DEBUG]", x, y, id)
    if visited[x + ZERO][y + ZERO] != -1:
        continue
    visited[x + ZERO][y + ZERO] = id

    for dx, dy in DIRS:
        nx = x + dx
        if nx < -ZERO or ZERO < nx:
            continue
        ny = y + dy
        if ny < -ZERO or ZERO < ny:
            continue
        if not is_black[nx + ZERO][ny + ZERO]:
            continue
        if visited[nx + ZERO][ny + ZERO] != -1:
            continue
        # print("[DEBUG]", "append", nx, ny, id)
        q.append((nx, ny, id))

# print("[DEBUG]", visited)
print(len(set(v for r in visited for v in r)) - 2)
