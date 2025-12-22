H, W = map(int, input().split())
A = [list(map(int, input().split())) for _ in range(H)]

stack = [(0, 0, {A[0][0]})]

cnt = 0
while stack:
    i, j, visited = stack.pop()
    if i == H-1 and j == W-1:
        cnt += 1
        continue

    if i+1 < H:
        a = A[i+1][j]
        if a not in visited:
            stack.append((i+1, j, visited | {a}))
    if j+1 < W:
        a = A[i][j+1]
        if a not in visited:
            stack.append((i, j+1, visited | {a}))

print(cnt)
