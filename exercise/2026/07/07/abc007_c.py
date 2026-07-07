# >>> atcoder-stat >>>
# started_at  = 2026-07-07T14:09:19+09:00
# solved_at   = 2026-07-07T14:16:12+09:00
# duration_ms = 413659
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

R, C = map(int, input().split())
sy, sx = map(int, input().split())
sy, sx = sy - 1, sx - 1
s = sy * C + sx
gy, gx = map(int, input().split())
gy, gx = gy - 1, gx - 1
g = gy * C + gx
S = [input().rstrip() for _ in range(R)]

q = [sy * C + sx]
d = [-1] * (R * C)
d[s] = 0
ADJ = [(1, 0), (-1, 0), (0, 1), (0, -1)]
for pos in q:
    y, x = divmod(pos, C)
    for dy, dx in ADJ:
        ny, nx = y + dy, x + dx
        npos = ny * C + nx
        if not (0 <= ny < R and 0 <= nx < C):
            continue
        if S[ny][nx] == "#":
            continue
        if d[npos] != -1:
            continue
        d[npos] = d[pos] + 1
        if npos == g:
            break
        q.append(npos)
    else:
        continue
    break

print(d[gy * C + gx])
