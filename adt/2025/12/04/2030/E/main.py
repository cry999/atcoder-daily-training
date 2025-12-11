N = int(input())
A = [input().strip() for _ in range(N)]
B = [[''] * N for _ in range(N)]

for x in range(N):
    for y in range(N):
        # n: 操作回数
        n = (min(x, y, N-1-x, N-1-y)+1) % 4

        nx, ny = x, y
        while n:
            nx, ny = ny, N-1-nx
            n -= 1

        B[nx][ny] = A[x][y]

print('\n'.join([''.join(row) for row in B]))
