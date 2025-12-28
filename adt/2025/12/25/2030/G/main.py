H, W, K = map(int, input().split())
S = [input() for _ in range(H)]

ans = float('inf')

# 縦方向に尺取り虫
for w in range(W):
    head, tail = 0, 0
    dotss_count = 1 if S[0][w] == '.' else 0
    white_count = 1 if S[0][w] == 'o' else 0
    black_count = 1 if S[0][w] == 'x' else 0
    while head < H:
        while tail-head < K-1 and tail+1 < H:
            tail += 1
            dotss_count += S[tail][w] == '.'
            white_count += S[tail][w] == 'o'
            black_count += S[tail][w] == 'x'
        if tail-head < K-1:
            break
        if black_count == 0:
            ans = min(ans, dotss_count)

        dotss_count -= S[head][w] == '.'
        white_count -= S[head][w] == 'o'
        black_count -= S[head][w] == 'x'
        head += 1

# 横方向に尺取り虫
for h in range(H):
    head, tail = 0, 0
    dotss_count = 1 if S[h][0] == '.' else 0
    white_count = 1 if S[h][0] == 'o' else 0
    black_count = 1 if S[h][0] == 'x' else 0
    while head < W:
        while tail-head < K-1 and tail+1 < W:
            tail += 1
            dotss_count += S[h][tail] == '.'
            white_count += S[h][tail] == 'o'
            black_count += S[h][tail] == 'x'
        if tail-head < K-1:
            break
        if black_count == 0:
            ans = min(ans, dotss_count)

        dotss_count -= S[h][head] == '.'
        white_count -= S[h][head] == 'o'
        black_count -= S[h][head] == 'x'
        head += 1


print(ans if ans < float('inf') else -1)
