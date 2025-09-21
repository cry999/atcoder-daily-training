import heapq

H, W, D = map(int, input().split())
S = [input() for _ in range(H)]
dp = [[float('inf')] * W for _ in range(H)]

q = []
for i in range(H):
    for j in range(W):
        if S[i][j] == 'H':
            heapq.heappush(q, (0, i, j))
            dp[i][j] = 0

# print(q)

while q:
    d, i, j = heapq.heappop(q)
    if i-1 >= 0 and S[i-1][j] != '#' and dp[i-1][j] > d+1:
        dp[i-1][j] = d+1
        if d+1 <= D:
            heapq.heappush(q, (d+1, i-1, j))
    if i+1 < H and S[i+1][j] != '#' and dp[i+1][j] > d+1:
        dp[i+1][j] = d+1
        if d+1 <= D:
            heapq.heappush(q, (d+1, i+1, j))
    if j-1 >= 0 and S[i][j-1] != '#' and dp[i][j-1] > d+1:
        dp[i][j-1] = d+1
        if d+1 <= D:
            heapq.heappush(q, (d+1, i, j-1))
    if j+1 < W and S[i][j+1] != '#' and dp[i][j+1] > d+1:
        dp[i][j+1] = d+1
        if d+1 <= D:
            heapq.heappush(q, (d+1, i, j+1))

print(sum(1 for i in range(H) for j in range(W) if dp[i][j] <= D))
# print(*[''.join(str(dp[i][j]) if dp[i][j] != float('inf')
#       else '#' for j in range(W)) for i in range(H)], sep='\n')
