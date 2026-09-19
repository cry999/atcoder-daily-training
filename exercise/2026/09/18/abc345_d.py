# >>> atcoder-stat >>>
# started_at  = 2026-09-18T18:57:51+09:00
# solved_at   = 2026-09-18T19:37:18+09:00
# duration_ms = 2367432
# target_ms   = 900000
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 1
# complexity  = 3
# impl        = 1
# verify      = 3
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline


N, H, W = map(int, input().split())
tiles = [tuple(map(int, input().split())) for _ in range(N)]


def check_area(s: int):
    """s に含まれるタイルの面積の合計が H*W であるかを確認する"""
    area_sum = 0
    for i in range(N):
        if (s >> i) & 1:
            h, w = tiles[i]
            area_sum += h * w
    return area_sum == H * W


board = [[False] * W for _ in range(H)]


def put(r: int, c: int, h: int, w: int, v: bool = True):
    # まずは指定の範囲が not v であることを確認する
    for i in range(r, min(H, r + h)):
        for j in range(c, min(W, c + w)):
            if board[i][j] == v:
                return False

    for i in range(r, min(H, r + h)):
        for j in range(c, min(W, c + w)):
            board[i][j] = v

    return True


def _can_fill(s: int, p0: int = 0):
    if s == 0:
        return all(all(row) for row in board)

    for p in range(p0, H * W):
        r, c = divmod(p, W)
        if board[r][c]:
            continue
        for i in range(N):
            if not (s >> i) & 1:
                continue

            h, w = tiles[i]
            for hh, ww in [(h, w), (w, h)]:
                if r + hh > H or c + ww > W:
                    continue
                if not put(r, c, hh, ww):
                    continue
                if _can_fill(s ^ (1 << i), p + 1):
                    return True
                put(r, c, hh, ww, False)
        return False
    return False


def can_fill(s: int):
    # board の初期化
    for h in range(H):
        for w in range(W):
            board[h][w] = False

    return _can_fill(s)


# s: 使用するタイルの集合
for s in range(1, 1 << N):
    if not check_area(s):
        continue
    print(f"[DEBUG] {s=:07b}")
    if can_fill(s):
        print("Yes")
        break
else:
    print("No")
