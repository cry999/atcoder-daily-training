import heapq


H, W, K = map(int, input().split())
C = [list(input()) for _ in range(H)]

max_black = 0
for bit in range(1 << H):
    CC = [C[i][:] for i in range(H)]
    # まずは行の処理
    count = 0
    for h in range(H):
        if not (1 << h) & bit:
            continue
        CC[h] = ['#'] * W
        count += 1
        if count == K:
            break

    blacks = sum(row.count('#') for row in CC)
    if count == K:
        max_black = max(max_black, blacks)
        continue

    # 残った回数分列を埋めていく
    queue = []
    for w in range(W):
        whites = sum(CC[h][w] == '.' for h in range(H))
        heapq.heappush(queue, -whites)
    for _ in range(count, K):
        blacks -= heapq.heappop(queue)
    max_black = max(max_black, blacks)

print(max_black)
