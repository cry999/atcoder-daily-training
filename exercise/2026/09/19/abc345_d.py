# >>> atcoder-stat >>>
# started_at  = 2026-09-19T09:50:27+09:00
# solved_at   = 2026-09-19T09:59:32+09:00
# duration_ms = 545649
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline


N, H, W = map(int, input().split())
tiles = [tuple(map(int, input().split())) for _ in range(N)]

board = [[False] * W for _ in range(H)]


def can_place(r: int, c: int, h: int, w: int):
    if r + h > H or c + w > W:
        return False
    for i in range(r, r + h):
        for j in range(c, c + w):
            if board[i][j]:
                return False
    return True


def place(r: int, c: int, h: int, w: int, fill: bool = True):
    for i in range(r, r + h):
        for j in range(c, c + w):
            board[i][j] = fill
    return


def dfs(s: int):
    if s == 0:
        return all(all(row) for row in board)

    for r in range(H):
        for c in range(W):
            if board[r][c]:
                continue
            # (r, c) にタイルを置く
            for i in range(N):
                if s & (1 << i) == 0:
                    continue
                h0, w0 = tiles[i]

                for h, w in [(h0, w0), (w0, h0)]:
                    if not can_place(r, c, h, w):
                        continue
                    place(r, c, h, w)
                    if dfs(s ^ (1 << i)):
                        return True
                    place(r, c, h, w, False)
            return False
    return False


def solve(s: int):
    area_sum = sum(h * w for i, (h, w) in enumerate(tiles) if s & (1 << i) != 0)
    if area_sum != H * W:
        return False

    return dfs(s)


for s in range(1, 1 << N):
    if solve(s):
        print("Yes")
        break
else:
    print("No")
