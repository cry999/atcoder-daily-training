# >>> atcoder-stat >>>
# started_at  = 2026-09-22T17:05:06+09:00
# solved_at   = 2026-09-22T17:15:15+09:00
# duration_ms = 609515
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, H, W = map(int, input().split())
tiles = [tuple(map(int, input().split())) for _ in range(N)]

# 重要な考察
# 1. 一番最初に出くわすあきますにおけるかだけを考える。
# 2. それ以外のあきますに置く可能性は、タイルを置く順番の問題にすぎない
# 3. 上記からざっくり計算量は O(N! HW) くらい。回転もあるので x2 だが定数倍は無視

board = [[0] * W for _ in range(H)]


def put(r: int, c: int, h: int, w: int, v: int):
    if r + h > H or c + w > W:
        return False

    for i in range(r, r + h):
        for j in range(c, c + w):
            if board[i][j] == v:
                return False

    for i in range(r, r + h):
        for j in range(c, c + w):
            board[i][j] = v
    return True


def dfs(rest: set[int]):
    for r in range(H):
        for c in range(W):
            if board[r][c] != 0:
                continue

            for i in rest:
                h0, w0 = tiles[i]
                for h, w in [(h0, w0), (w0, h0)]:
                    if not put(r, c, h, w, 1):
                        continue
                    if dfs(rest - {i}):
                        return True
                    put(r, c, h, w, 0)
            return False

    # ここまできたということは全てのますが埋まっているということ
    return True


if dfs(set(range(N))):
    print("Yes")
else:
    print("No")
