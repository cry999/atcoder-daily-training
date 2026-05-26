from collections import deque

WHITE = -2


def conv(c: str) -> int:
    if c == "#":
        return -1
    return WHITE


H, W = map(int, input().split())
S = [list(map(conv, input())) for _ in range(H)]


def count(h: int, w: int, t: int = 0) -> int:
    adj = 0
    adj += h > 0 and WHITE < S[h - 1][w] < t
    adj += h < H - 1 and WHITE < S[h + 1][w] < t
    adj += w > 0 and WHITE < S[h][w - 1] < t
    adj += w < W - 1 and WHITE < S[h][w + 1] < t
    return adj


q = deque()
for h in range(H):
    for w in range(W):
        if S[h][w] != WHITE:
            continue
        if count(h, w) == 1:
            q.append((0, h, w))

while q:
    t, h, w = q.popleft()

    if count(h, w, t) != 1:
        continue
    if S[h][w] != WHITE:
        continue

    S[h][w] = t
    # print(f"fill ({h}, {w}) with {t}")
    # 隣接するますをキューに候補点として追加
    for dh, dw in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nh, nw = h + dh, w + dw
        if not (0 <= nh < H and 0 <= nw < W):
            continue
        if S[nh][nw] != WHITE:
            continue

        q.append((t + 1, nh, nw))

# for s in S:
#     print(*map(lambda x: "." if x == WHITE else "#", s))

ans = sum(c != WHITE for s in S for c in s)
print(ans)
