N = int(input())

B = [[""] * N for _ in range(N)]
B[N // 2][N // 2] = "T"

i = 1
x, y = 0, 0
dx, dy = 1, 0
while i < N * N:
    B[x][y] = str(i)

    nx, ny = x + dx, y + dy
    if not (0 <= nx < N and 0 <= ny < N) or B[nx][ny] != "":
        dx, dy = -dy, dx
        nx, ny = x + dx, y + dy

    x, y = nx, ny
    i += 1

for row in B:
    print(*row)
