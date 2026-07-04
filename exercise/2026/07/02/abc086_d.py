# >>> atcoder-stat >>>
# started_at  = 2026-07-02T11:55:10+09:00
# solved_at   = 2026-07-02T11:55:10+09:00
# duration_ms = 7560000
# target_ms   = 900000
# ac          = true
# editorial   = true
# knowledge   = 2
# translation = 2
# complexity  = 3
# impl        = 1
# verify      = 1
# <<< atcoder-stat <<<
N, K = map(int, input().split())

blacks = [[0] * (4 * K + 1) for _ in range(4 * K + 1)]

for _ in range(N):
    raw_x, raw_y, c = input().split()
    x, y = int(raw_x), int(raw_y)
    if c == "W":
        y += K

    x %= 2 * K
    y %= 2 * K

    blacks[x][y] += 1
    blacks[x + 2 * K][y] += 1
    blacks[x][y + 2 * K] += 1
    blacks[x + 2 * K][y + 2 * K] += 1

for i in range(4 * K + 1):
    for j in range(4 * K):
        blacks[i][j + 1] += blacks[i][j]
for i in range(4 * K):
    for j in range(4 * K + 1):
        blacks[i + 1][j] += blacks[i][j]


def area(i: int, j: int, board: list[list[int]]):
    n = 0
    max_i, max_j = i + K - 1, j + K - 1
    # print(f"[DEBUG]  {i=} {j=} {max_i=} {max_j=}")
    if max_i >= 0 and max_j >= 0:
        n += board[max_i][max_j]
    if i > 0 and max_j >= 0:
        n -= board[i - 1][max_j]
    if j > 0 and max_i >= 0:
        n -= board[max_i][j - 1]
    if i > 0 and j > 0:
        n += board[i - 1][j - 1]
    return n


ans = 0
for i in range(2 * K):
    for j in range(2 * K):
        # (i, j) を左下とする白の領域を動かしていく
        black = area(i, j, blacks) + area(i + K, j + K, blacks)
        ans = max(ans, black)

print(ans)
