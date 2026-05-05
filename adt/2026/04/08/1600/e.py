N = 9
A = [list(map(int, input().split())) for _ in range(N)]

# 行チェック
for r in range(N):
    check = [False] * N
    for c in range(N):
        x = A[r][c] - 1
        if check[x]:
            print("No")
            exit()
        check[x] = True

# 列チェック
for c in range(N):
    check = [False] * N
    for r in range(N):
        x = A[r][c] - 1
        if check[x]:
            print("No")
            exit()
        check[x] = True


# 3x3 チェッく
for offset in range(N):
    offset_row, offset_col = offset // 3, offset % 3
    check = [False] * N
    for pos in range(N):
        r = pos // 3 + offset_row * 3
        c = pos % 3 + offset_col * 3
        x = A[r][c] - 1
        if check[x]:
            print("No")
            exit()
        check[x] = True

print("Yes")
