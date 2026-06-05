from collections import deque

N = int(input())
S = [input() for _ in range(N)]

dist = [[[[float("inf")] * N for _ in range(N)] for _ in range(N)] for _ in range(N)]

pi1, pj1 = -1, -1
pi2, pj2 = -1, -1
for i in range(N):
    for j in range(N):
        if S[i][j] == "P":
            if pi1 == -1:
                pi1, pj1 = i, j
            else:
                pi2, pj2 = i, j


dist[pi1][pj1][pi2][pj2] = 0
q = deque()
q.append((pi1, pj1, pi2, pj2, 0))

DIRS = [(0, -1), (0, 1), (-1, 0), (1, 0)]
while q:
    ci1, cj1, ci2, cj2, d = q.popleft()
    if ci1 == ci2 and cj1 == cj2:
        print(d)
        break

    for di, dj in DIRS:
        ni1, nj1 = ci1 + di, cj1 + dj
        if not (0 <= ni1 < N and 0 <= nj1 < N):
            # 移動しない
            ni1, nj1 = ci1, cj1
        if S[ni1][nj1] == "#":
            # 移動しない
            ni1, nj1 = ci1, cj1

        ni2, nj2 = ci2 + di, cj2 + dj
        if not (0 <= ni2 < N and 0 <= nj2 < N):
            # 移動しない
            ni2, nj2 = ci2, cj2
        if S[ni2][nj2] == "#":
            # 移動しない
            ni2, nj2 = ci2, cj2

        if dist[ni1][nj1][ni2][nj2] <= d + 1:
            continue
        dist[ni1][nj1][ni2][nj2] = d + 1

        if ni1 == ni2 and nj1 == nj2:
            print(d + 1)
            break
        q.append((ni1, nj1, ni2, nj2, d + 1))
    else:
        continue
    break
else:
    print(-1)
