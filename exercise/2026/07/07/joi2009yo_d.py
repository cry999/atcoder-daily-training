import sys

sys.setrecursionlimit(10**6)

M = int(input())
N = int(input())
S = [list(map(int, input().split())) for _ in range(N)]

visited = [False] * (N * M)

ADJ = [(0, 1), (0, -1), (1, 0), (-1, 0)]


def dfs(i: int, j: int):
    if visited[i * M + j] or S[i][j] == 0:
        return 0
    visited[i * M + j] = True

    res = 0
    for di, dj in ADJ:
        ni, nj = i + di, j + dj
        if not (0 <= ni < N and 0 <= nj < M):
            continue
        if S[ni][nj] == 0:
            continue
        if visited[ni * M + nj]:
            continue
        res = max(res, dfs(ni, nj))

    visited[i * M + j] = False
    return res + 1


ans = 0
for p in range(N * M):
    i, j = divmod(p, M)
    if S[i][j] == 0:
        continue
    ans = max(ans, dfs(i, j))
print(ans)
