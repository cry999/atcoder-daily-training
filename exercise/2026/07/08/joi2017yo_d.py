N, M = map(int, input().split())
A = [int(input()) - 1 for _ in range(N)]

INF = 10**9
dp = [INF] * (1 << M)
dp[0] = 0
cnt = [[0] * (N + 1) for _ in range(M)]
for i in range(N):
    cnt[A[i]][i + 1] += 1

for i in range(N):
    for j in range(M):
        cnt[j][i + 1] += cnt[j][i]

for s in range(1 << M):  # 現在の左側の並べ状況
    # 左に並べられているぬいぐるみの数
    left = sum(cnt[j][N] for j in range(M) if s & (1 << j))
    for j in range(M):  # 次におく種類
        if s & (1 << j):
            # すでに置かれているのでスキップ
            continue
        ns = s | (1 << j)
        right = left + cnt[j][N] - 1
        # [left, right] の範囲にぬいぐるみ j をおく。
        # この範囲にある j 以外のぬいぐるみの数が移動しないといけない個数。
        move = cnt[j][N] - (cnt[j][right + 1] - cnt[j][left])
        dp[ns] = min(dp[ns], dp[s] + move)
print(dp[(1 << M) - 1])
