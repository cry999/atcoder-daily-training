# >>> atcoder-stat >>>
# started_at  = 2026-09-19T10:15:58+09:00
# solved_at   = 2026-09-19T10:51:18+09:00
# duration_ms = 2120507
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 1
# complexity  = 3
# impl        = 1
# verify      = 3
# <<< atcoder-stat <<<
import functools

A = [list(map(int, input().split())) for _ in range(3)]

TAKAHASHI = 0
AOKI = 1

LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8), # 横
    (0, 3, 6), (1, 4, 7), (2, 5, 8), # 縦
    (0, 4, 8), (2, 4, 6), # 斜め
)

@functools.cache
def dfs(c: tuple[int], cur: int):
    for x, y, z in LINES:
        if c[x] == c[y] == c[z] != -1:
            return c[x]

    if all(c[i] != -1 for i in range(9)):
        takahashi, aoki = 0, 0
        for p in range(9):
            i, j = divmod(p, 3)
            if c[p] == TAKAHASHI:
                takahashi += A[i][j]
            else:
                aoki += A[i][j]
        return TAKAHASHI if takahashi > aoki else AOKI

    opp = 1 - cur
    for p in range(9):
        if c[p] != -1:
            continue

        nc = tuple(c[i] if i != p else cur for i in range(9))
        if dfs(nc, opp) == cur:
            # 自分が勝てる手順があればそれを選択
            return cur

    # この状態から自分が勝てる手順がない
    return opp


if dfs(tuple([-1] * 9), TAKAHASHI) == TAKAHASHI:
    print("Takahashi")
else:
    print("Aoki")
