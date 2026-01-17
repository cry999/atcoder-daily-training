from collections import deque


H, W = map(int, input().split())

A = [input() for _ in range(H)]
door_states = ["o", "x"]

visited = [[[False] * W for _ in range(H)] for _ in range(2)]

si, sj = -1, -1
for i in range(H):
    for j in range(W):
        if A[i][j] == "S":
            si, sj = i, j
            break
    else:
        continue
    break

visited[0][si][sj] = True
queue = deque()
queue.append((0, si, sj, 0))

while queue:
    dist, i, j, door_state = queue.popleft()

    for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        ni, nj = i + di, j + dj
        if not (0 <= ni < H and 0 <= nj < W):
            continue
        if A[ni][nj] == "#":
            continue
        if A[ni][nj] == door_states[1 - door_state]:
            continue
        if A[ni][nj] == "G":
            print(dist + 1)
            exit()
        n_door_state = door_state
        if A[ni][nj] == "?":
            n_door_state = 1 - door_state

        if visited[n_door_state][ni][nj]:
            continue
        # print(f"{i=}, {j=}, {door_state=} -> {ni=}, {nj=}, {n_door_state=}")
        visited[n_door_state][ni][nj] = True
        queue.append((dist + 1, ni, nj, n_door_state))

print("-1")
