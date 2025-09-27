import heapq


N, M = map(int, input().split())
dp = [[-1] * N for _ in range(N)]

dp[0][0] = 0

# M で移動できる (dx, dy) の組み合わせを全列挙
# これは移動開始前の点に依存しない
diff = []
for dx in range(N):
    for dy in range(N):
        if M != dx * dx + dy * dy:
            continue

        diff.append((dx, dy))
        if dx != 0:
            diff.append((-dx, dy))
        if dy != 0:
            diff.append((dx, -dy))
        if dx != 0 and dy != 0:
            diff.append((-dx, -dy))

queue = []  # (op, x, y)
heapq.heappush(queue, (0, 0, 0))

while queue:
    op, x, y = heapq.heappop(queue)
    for dx, dy in diff:
        nop, nx, ny = op + 1, x + dx, y + dy
        if nx < 0 or nx >= N or ny < 0 or ny >= N:
            continue
        if -1 < dp[nx][ny] <= nop:
            continue
        dp[nx][ny] = nop
        heapq.heappush(queue, (nop, nx, ny))

print('\n'.join(' '.join(map(str, row)) for row in dp))
