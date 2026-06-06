from collections import defaultdict

H, W = map(int, input().split())
C = [list(input()) for _ in range(H)]

hist_row = [defaultdict(int) for _ in range(H)]
for i in range(H):
    for j in range(W):
        hist_row[i][C[i][j]] += 1

hist_col = [defaultdict(int) for _ in range(W)]
for j in range(W):
    for i in range(H):
        hist_col[j][C[i][j]] += 1

cur_h, cur_w = H, W
ans = H * W
while True:
    nxt_h, nxt_w = cur_h, cur_w
    rm_from_col = defaultdict(int)
    for i in range(H):
        if len(hist_row[i]) == 1 and cur_w > 1:
            k, v = hist_row[i].popitem()
            if v != cur_w:
                hist_row[i][k] = v
            else:
                rm_from_col[k] += 1
                ans -= v
                nxt_h -= 1

    rm_from_row = defaultdict(int)
    for j in range(W):
        if len(hist_col[j]) == 1 and cur_h > 1:
            k, v = hist_col[j].popitem()
            if v != cur_h:
                hist_col[j][k] = v
            else:
                rm_from_row[k] += 1
                ans -= v
                nxt_w -= 1

    cur_h, cur_w = nxt_h, nxt_w
    if rm_from_col or rm_from_row:
        for j in range(W):
            for k, v in rm_from_col.items():
                hist_col[j][k] -= v
                if hist_col[j][k] <= 0:
                    del hist_col[j][k]

        for i in range(H):
            for k, v in rm_from_row.items():
                hist_row[i][k] -= v
                if hist_row[i][k] <= 0:
                    del hist_row[i][k]

        continue

    break

print(cur_h * cur_w)
