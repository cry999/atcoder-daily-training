import heapq
import sys

sys.setrecursionlimit(10**7)


H, W, T = map(int, input().split())
A = [input() for _ in range(H)]

nodes = []
start: tuple[int, int] = (-1, -1)
goal: tuple[int, int] = (-1, -1)
for h in range(H):
    for w in range(W):
        if A[h][w] in ("#", "."):
            continue
        if A[h][w] == "S":
            start = (h, w)
        elif A[h][w] == "G":
            goal = (h, w)
        else:
            nodes.append((h, w))

nodes = [start] + nodes + [goal]
node_indexes = {pos: i for i, pos in enumerate(nodes)}

dist = [[float("inf")] * len(nodes) for _ in nodes]

visited = [[False] * W for _ in range(H)]
for i, (sh, sw) in enumerate(nodes):
    for h in range(H):
        for w in range(W):
            visited[h][w] = False

    queue = [(0, sh, sw)]
    dist[i][i] = 0
    while queue:
        cost, h, w = heapq.heappop(queue)
        if visited[h][w]:
            continue
        visited[h][w] = True

        if (h, w) in node_indexes:
            dist[i][node_indexes[(h, w)]] = cost

        for dh, dw in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nh, nw = h + dh, w + dw
            if not (0 <= nh < H and 0 <= nw < W):
                continue
            if visited[nh][nw]:
                continue
            if A[nh][nw] == "#":
                continue
            heapq.heappush(queue, (cost + 1, nh, nw))


# dp[i][bit]: i 番目のノードにいて、bit で表現されるノードに訪問済みの時の最小移動コスト
dp = [[float("inf")] * (1 << len(nodes)) for _ in nodes]
dp[0][1] = 0

for bit in range(1 << len(nodes)):
    for j in range(len(nodes)):
        if dp[j][bit] == float("inf"):
            continue
        # j -> k に移動する。
        for k in range(len(nodes)):
            if bit & (1 << k):
                continue
            dp[k][bit | (1 << k)] = min(
                dp[k][bit | (1 << k)],
                dp[j][bit] + dist[j][k],
            )

ans = -1
for bit in range(1 << len(nodes)):
    if dp[len(nodes) - 1][bit] > T:
        # コストオーバーは除外
        continue
    cnt = bit.bit_count() - 2  # S, G を除く
    ans = max(ans, cnt)

print(ans)
