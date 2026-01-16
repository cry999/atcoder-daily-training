from collections import deque
import sys

sys.setrecursionlimit(10**7)


H, W = map(int, input().split())
S = [input() for _ in range(H)]

free = [[0] * W for _ in range(H)]


def next_to_magnet(i: int, j: int) -> bool:
    if i > 0 and S[i - 1][j] == "#":
        return True
    if i + 1 < H and S[i + 1][j] == "#":
        return True
    if j > 0 and S[i][j - 1] == "#":
        return True
    return j + 1 < W and S[i][j + 1] == "#"


# magnet に隣接するマスは単純な訪問済みとしては計算できないので、
# 調査番号で管理する。
ans = 1
visited = [[-1] * W for _ in range(H)]
for i in range(H):
    for j in range(W):
        # 左上から行→ 列の順番で自由度を求めていく。
        # まずは、マグネットに隣接しているものの自由度を -1 にする。
        if S[i][j] == "#":
            continue
        if next_to_magnet(i, j):
            free[i][j] = -1
            continue
        # マグネットと隣り合っていない場合、左か上がマグネットに隣接した値でなければ
        # 自由度は同じになる。
        if i > 0 and free[i - 1][j] != -1:
            free[i][j] = free[i - 1][j]
            continue
        if j > 0 and free[i][j - 1] != -1:
            free[i][j] = free[i - 1][j]
            continue

        n = i * W + j
        # print(f"{i=}, {j=}, {n=}")
        cnt = 0
        queue = deque()
        queue.append((i, j))
        visited[i][j] = n
        while queue:
            r, c = queue.popleft()
            # print(f"  count {r=}, {c=}")
            cnt += 1

            for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nr, nc = r + dr, c + dc
                if not (0 <= nr < H and 0 <= nc < W):
                    continue
                if S[nr][nc] == "#":
                    continue
                if next_to_magnet(nr, nc):
                    if visited[nr][nc] == n:
                        # 今回の探索番号と一致しているなら訪問済みとする。
                        continue
                    # そうでない場合、cnt をカウントアップして探索済みにする
                    cnt += 1
                    visited[nr][nc] = n
                    # print(f"  count {nr=}, {nc=}")
                    continue

                if visited[nr][nc] != -1:
                    # 訪問済み
                    continue
                visited[nr][nc] = n
                queue.append((nr, nc))
        ans = max(ans, cnt)
        # print(f"  {cnt=}")
print(ans)
