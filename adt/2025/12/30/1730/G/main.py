from collections import deque


N, M = map(int, input().split())
S = [input() for _ in range(N)]

visited = [[False] * M for _ in range(N)]

queue = deque()
queue.append((1, 1))
visited[1][1] = True

while queue:
    i, j = queue.popleft()
    # print(f"processing ({i=}, {j=})")

    # 上下左右に通ってない通路があるか？
    for di, dj in [(-1, 0), (1, 0), (0, 1), (0, -1)]:
        # print(f"  check direction ({di=}, {dj=})")
        ti = i + di
        tj = j + dj
        not_visited = False
        while 0 <= ti < N and 0 <= tj < M:
            if S[ti][tj] == "#":
                break
            if not visited[ti][tj]:
                not_visited = True
                break
            # print(f"  already visited ({ti=}, {tj=})")
            ti += di
            tj += dj

        if not_visited:
            # print(f"  going direct ({di=}, {dj=})")
            ti = i + di
            tj = j + dj
            while 0 <= ti < N and 0 <= tj < M:
                # print(f"    visiting ({ti=}, {tj=})")
                if S[ti][tj] == "#":
                    queue.append((ti - di, tj - dj))
                    break
                visited[ti][tj] = True
                ti += di
                tj += dj

# print(visited)
cnt = 0
for i in range(N):
    for j in range(M):
        cnt += visited[i][j] and S[i][j] == "."
print(cnt)
