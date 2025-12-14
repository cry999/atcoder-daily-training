from collections import deque, defaultdict


H, W = map(int, input().split())

S = [input() for _ in range(H)]

dist = [[float('inf')] * W for _ in range(H)]


# warps の数が HW だと、計算量は O((HW)^2) になるので TLE する。
# 一度使ったワープマスを使わないようにすれば良い。
warps = defaultdict(list)
for i in range(H):
    for j in range(W):
        c = S[i][j]
        if c in ('#', '.'):
            continue
        # print(f'warp found: {c} at ({i=}, {j=})')
        warps[c].append((i, j))

# print(f'warps: {warps}')
queue = deque([(0, 0, 0)])  # (cost, i, j)
dist[0][0] = 0
dijs = [(1, 0), (0, 1), (-1, 0), (0, -1)]

used_warps = [False] * 26


while queue:
    cost, i, j = queue.popleft()
    # print(f'{cost=}, {i=}, {j=}')
    if dist[i][j] < cost:
        continue
    if i == H-1 and j == W-1:
        # print('  reach goal')
        # ゴールに到達したら終了
        break

    for di, dj in dijs:
        ni, nj = i+di, j+dj
        # print(f'  try ({ni=}, {nj=})')
        if ni < 0 or H <= ni or nj < 0 or W <= nj:
            # 迷路の外にはでられない
            # print('    out of range')
            continue
        if S[ni][nj] == '#':
            # 壁には進めない
            # print('    wall')
            continue
        if dist[ni][nj] <= cost+1:
            # 到達コストが高くなるなら無視
            # print('    higher cost')
            continue
        dist[ni][nj] = cost+1
        queue.append((cost+1, ni, nj))

    if S[i][j] in ('#', '.'):
        continue

    # ワープマス
    if used_warps[ord(S[i][j])-ord('a')]:
        # すでに使ったワープマスなので無視
        continue

    used_warps[ord(S[i][j])-ord('a')] = True

    for ni, nj in warps[S[i][j]]:
        # print(f'  try warp ({ni=}, {nj=})')
        if ni == i and nj == j:
            # 今いる場所は無視
            # print('    same place')
            continue
        if dist[ni][nj] <= cost+1:
            # 到達コストが高くなるなら無視
            # print('    higher cost (warp)')
            continue
        dist[ni][nj] = cost+1
        queue.append((cost+1, ni, nj))

if dist[H-1][W-1] == float('inf'):
    print(-1)
else:
    print(dist[H-1][W-1])
