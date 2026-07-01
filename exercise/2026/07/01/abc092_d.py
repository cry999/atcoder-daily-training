# >>> atcoder-stat >>>
# started_at  = 2026-07-01T14:42:42+09:00
# solved_at   = 2026-07-01T15:16:25+09:00
# duration_ms = 2023607
# target_ms   = 900000
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 2
# complexity  = 2
# impl        = 1
# verify      = 1
# <<< atcoder-stat <<<
A, B = map(int, input().split())

K = 50

grid = [["#" if k < K else "."] * (2 * K) for k in range(2 * K)]

for a in range(A - 1):
    i, j = divmod(a, K)
    grid[2 * i][2 * j] = "."

for b in range(B - 1):
    i, j = divmod(b, K)
    grid[2 * i + K + 1][2 * j] = "#"

print(2 * K, 2 * K)
print("\n".join("".join(r) for r in grid))
