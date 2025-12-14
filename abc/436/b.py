from collections import deque

N = int(input())

queue = deque()
queue.append((0, (N-1)//2, 1))

board = [[0]*N for _ in range(N)]
board[0][(N-1)//2] = 1

while queue:
    r, c, k = queue.popleft()

    nr, nc = (r-1+N) % N, (c+1) % N
    if board[nr][nc] > 0:
        nr, nc = (r+1) % N, c
    if board[nr][nc] > 0:
        continue

    board[nr][nc] = k+1
    queue.append((nr, nc, k+1))
    # print(nr, nc, k)

print('\n'.join(' '.join(map(str, board[i])) for i in range(N)))
