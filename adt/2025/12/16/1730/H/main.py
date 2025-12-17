H, W, N = map(int, input().split())

# dp O(HW); WA
# S = {}
#
# for _ in range(N):
#     a, b = map(int, input().split())
#     if a-1 not in S:
#         S[a-1] = set()
#     S[a-1].add(b-1)
#
# dp = [[0] * W for _ in range(H)]
#
# for h in range(H):
#     for w in range(W):
#         if h in S and w in S[h]:
#             dp[h][w] = 0
#             continue
#
#         if h > 0 and w > 0:
#             dp[h][w] = min(dp[h-1][w], dp[h][w-1]) + 1
#         else:
#             dp[h][w] = 1
#
# ans = sum(sum(row) for row in dp)
# print(ans)

# 累積和 + 二分探索 O(HW log(min(H, W)))
# S は (1, 1) から (H, W) までの穴の個数の累積和
HOLE = [[0] * (W+1) for _ in range(H+1)]

for _ in range(N):
    a, b = map(int, input().split())
    HOLE[a][b] += 1

for h in range(H):
    for w in range(W+1):
        HOLE[h+1][w] += HOLE[h][w]

for w in range(W):
    for h in range(H+1):
        HOLE[h][w+1] += HOLE[h][w]


def hole(h1: int, w1: int, h2: int, w2: int) -> int:
    '''(h1, w1) から (h2, w2) までの穴の個数を返す。'''
    return HOLE[h2][w2] - HOLE[h2][w1-1] - HOLE[h1-1][w2] + HOLE[h1-1][w1-1]

# (h, w) を左上の頂点とする正方形を数える。
# (h, w) を左上の頂点として、(h+n, w+n) を対角にもつ正方形について考える。


ans = 0
for h in range(1, H+1):
    for w in range(1, W+1):
        # print(f'=== {h=}, {w=} ===')
        # そもそも (h, w) が穴なら考えるまでもなくスキップ
        if hole(h, w, h, w):
            # print(f'({h}, {w}) is hole')
            continue

        lo, hi = 0, min(H-h, W-w)+1
        while hi-lo > 1:
            mi = (lo+hi)//2
            if hole(h, w, h+mi, w+mi):
                # 穴があるなら縮める
                hi = mi
            else:
                lo = mi
        # print(f'{lo=}, {hi=}')
        ans += hi

print(ans)
