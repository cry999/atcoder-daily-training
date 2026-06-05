from sortedcontainers import SortedList

H, W, Q = map(int, input().split())

wall_by_row = [SortedList(range(W)) for _ in range(H)]
wall_by_col = [SortedList(range(H)) for _ in range(W)]

for _ in range(Q):
    r, c = map(int, input().split())
    r, c = r - 1, c - 1

    i = wall_by_row[r].bisect_left(c)
    if 0 <= i < len(wall_by_row[r]) and wall_by_row[r][i] == c:
        # (r, c) に壁がある場合
        wall_by_row[r].remove(c)
        wall_by_col[c].remove(r)
    else:
        # (r, c) に壁がない場合
        # 右
        if i < len(wall_by_row[r]):
            right_c = wall_by_row[r][i]
            wall_by_row[r].remove(right_c)
            wall_by_col[right_c].remove(r)

        # 左
        if 0 <= i - 1:
            left_c = wall_by_row[r][i - 1]
            wall_by_row[r].remove(left_c)
            wall_by_col[left_c].remove(r)

        j = wall_by_col[c].bisect_left(r)
        # 下
        if j < len(wall_by_col[c]):
            down_r = wall_by_col[c][j]
            wall_by_col[c].remove(down_r)
            wall_by_row[down_r].remove(c)

        # 上
        if j - 1 >= 0:
            up_r = wall_by_col[c][j - 1]
            wall_by_col[c].remove(up_r)
            wall_by_row[up_r].remove(c)

print(sum(len(walls) for walls in wall_by_row))
