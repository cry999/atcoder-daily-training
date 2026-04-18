from sys import stdin

input = stdin.readline

H, W = map(int, input().split())
S = [input() for _ in range(H)]

visited = [0] * (H * W)

diffs = [(0, 1), (0, -1), (1, 0), (-1, 0)]

si, sj = 0, 0
for i in range(H):
    for j in range(W):
        if S[i][j] == "S":
            si, sj = i, j
            break
    else:
        continue
    break

visited[si * W + sj] = 0b1111

stack = [[si, sj, -1, 0]]
while stack:
    i, j, prev_dir, next_dir = stack[-1]
    if next_dir >= 4:
        stack.pop()
        continue
    stack[-1][-1] += 1
    di, dj = diffs[next_dir]
    ni, nj = i + di, j + dj
    if not (0 <= ni < H and 0 <= nj < W):
        continue
    if S[ni][nj] == "#":
        continue
    if S[i][j] == "o" and next_dir != prev_dir:
        continue
    if S[i][j] == "x" and next_dir == prev_dir:
        continue
    nidx = ni * W + nj
    if visited[nidx] & (1 << next_dir):
        continue
    if S[ni][nj] in "ox":
        visited[nidx] |= 1 << next_dir
    else:
        visited[nidx] = 0b1111

    stack.append([ni, nj, next_dir, 0])

    if S[ni][nj] == "G":
        break


if stack:
    print("Yes")
    out = ""
    for _, _, a, _ in stack[1:]:
        if a == 0:
            out += "R"
        elif a == 1:
            out += "L"
        elif a == 2:
            out += "D"
        else:
            out += "U"
    print(out)
else:
    print("No")
