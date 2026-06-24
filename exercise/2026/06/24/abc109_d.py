import sys

input = sys.stdin.readline


H, W = map(int, input().split())
A = [list(map(int, input().split())) for _ in range(H)]

ans = []

# === hamayan さんの解法 ===
# https://blog.hamayanhamayan.com/entry/2018/09/09/004851

for h in range(H):
    for w in range(W - 1):
        if A[h][w] % 2 == 1:
            A[h][w] -= 1
            A[h][w + 1] += 1
            ans.append((h + 1, w + 1, h + 1, w + 2))

for h in range(H - 1):
    if A[h][W - 1] % 2 == 1:
        A[h][W - 1] -= 1
        A[h + 1][W - 1] += 1
        ans.append((h + 1, W, h + 2, W))

# === 以下、自分で考えた螺旋解法 ===
# traces = []
# visited = [[False] * W for _ in range(H)]
# # 螺旋状に回ることで、各マス最大 1 回しか移動させないを守る。
# q = [(0, 0, 0, 1, False)]
# visited[0][0] = True
# for h, w, dh, dw, carrying in q:
#     # print(f"[DEBUG] {h=}, {w=}, ({dh=}, {dw=}) {carrying=}")
#     if 0 <= h < H and 0 <= w < W and A[h][w] % 2 == 1:
#         if carrying:
#             # 移動中なら、(nh, nw) に置く
#             A[h][w] += 1
#             ans.extend(traces)
#             # print(f"[DEBUG]   put  @({h}, {w})")
#         else:
#             # print(f"[DEBUG]   pick @({h}, {w})")
#             A[h][w] -= 1
#             traces = []
#
#         carrying = not carrying
#         # print(f"[DEBUG] {h=}, {w=}, {carrying=}, {A=}")
#
#     nh, nw = h + dh, w + dw
#     if dw == 1 and (w + dw >= W or visited[nh][nw]):
#         dh, dw = 1, 0
#         nh, nw = h + dh, w + dw
#     elif dw == -1 and (w + dw < 0 or visited[nh][nw]):
#         dh, dw = -1, 0
#         nh, nw = h + dh, w + dw
#     elif dh == 1 and (h + dh >= H or visited[nh][nw]):
#         dh, dw = 0, -1
#         nh, nw = h + dh, w + dw
#     elif dh == -1 and (h + dh < 0 or visited[nh][nw]):
#         dh, dw = 0, 1
#         nh, nw = h + dh, w + dw
#
#     # print(f"[DEBUG] -> {nh=}, {nw=}, {dh=}, {dw=}")
#
#     if not (0 <= nh < H and 0 <= nw < W) or visited[nh][nw]:
#         continue
#
#     if carrying:
#         traces.append((h + 1, w + 1, nh + 1, nw + 1))
#
#     q.append((nh, nw, dh, dw, carrying))
#     visited[nh][nw] = True

print(len(ans))
for h1, w1, h2, w2 in ans:
    print(h1, w1, h2, w2)

# print(f"[DEBUG] === A ===")
# for a in A:
#     print(f"[DEBUG] {a}")
