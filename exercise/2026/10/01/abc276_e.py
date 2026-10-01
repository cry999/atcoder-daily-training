# >>> atcoder-stat >>>
# started_at  = 2026-10-01T08:46:31+09:00
# solved_at   = 2026-10-01T09:02:09+09:00
# duration_ms = 938480
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


H, W = map(int, input().split())
C = [list(input().rstrip()) for _ in range(H)]

# 考察
# 1. S からスタートする最初の 4 方向。これらの交わる点があればいい?

# visited[p] := p を訪れ他のは、最初どの方向を向いていた経路か?
visited = [-1] * (H * W)

s = 0
q = []
for p in range(H * W):
    h, w = divmod(p, W)
    if C[h][w] == "S":
        s = p
        visited[s] = -2
        if h > 0 and C[h - 1][w] != "#":
            q.append(p - W)
            visited[p - W] = 0
        if h + 1 < H and C[h + 1][w] != "#":
            q.append(p + W)
            visited[p + W] = 1
        if w > 0 and C[h][w - 1] != "#":
            q.append(p - 1)
            visited[p - 1] = 2
        if w + 1 < W and C[h][w + 1] != "#":
            q.append(p + 1)
            visited[p + 1] = 3
        break
print(f"[DEBUG] {visited=}")
DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
for p in q:
    h, w = divmod(p, W)
    for dh, dw in DIRS:
        nh, nw = h + dh, w + dw
        np = nh * W + nw
        if not (0 <= nh < H and 0 <= nw < W) or np == s:
            continue
        if C[nh][nw] == "#":
            continue
        if visited[np] == visited[p]:
            continue
        if visited[np] >= 0:
            print(f"[DEBUG] meet {(h, w)=} and {(nh, nw)=}")
            print("Yes")
            exit()
        visited[np] = visited[p]
        q.append(np)

print("No")
