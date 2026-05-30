from collections import deque

H, W = map(int, input().split())

S = [list(input()) for _ in range(H)]
T = [[""] * W for i in range(H)]

NEIGHBORS = [
    (-1, 0),
    (-1, -1),
    (-1, 1),
    # (0, 0),
    (0, -1),
    (0, 1),
    (1, 0),
    (1, -1),
    (1, 1),
]

# 1 回変化した後、# になっている点はこの後は奇数回の変更で必ず # に戻る。
# なので 10^100 回変化させた後は . になる。
#
# 1 回変化したあと . になっている点はこの時点で一番近い # から伝搬するので
# それによって # になるタイミングが偶数か奇数かを見極める。
for i in range(H):
    for j in range(W):
        if S[i][j] == ".":
            for di, dj in NEIGHBORS:
                if 0 <= i + di < H and 0 <= j + dj < W and S[i + di][j + dj] == "#":
                    T[i][j] = "#"
                    break
            else:
                T[i][j] = "."
        else:
            T[i][j] = "."


ans = [[""] * W for i in range(H)]
dist = [[-1] * W for i in range(H)]
q = deque()
for i in range(H):
    for j in range(W):
        if T[i][j] == ".":
            pass
        else:
            ans[i][j] = "."
            q.append((i, j, 0))
            dist[i][j] = 0

while q:
    i, j, d = q.popleft()

    for di, dj in NEIGHBORS:
        ni, nj = i + di, j + dj
        if not (0 <= ni < H and 0 <= nj < W):
            continue
        if 0 <= dist[ni][nj] <= d + 1:
            continue
        dist[ni][nj] = d + 1
        ans[ni][nj] = "#" if (d + 1) % 2 == 1 else "."
        q.append((ni, nj, d + 1))

for i in range(H):
    for j in range(W):
        if ans[i][j] == "":
            # 到達できない点、というか最初全部黒 or 白で塗り尽くされてた場合
            ans[i][j] = "."

print("\n".join("".join(row) for row in ans))
