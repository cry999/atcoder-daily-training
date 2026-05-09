N = int(input())
# i, j = min(i, j), max(i, j); D[i][j-i-1]
D = [list(map(int, input().split())) for _ in range(N - 1)]

dp = [0] * (1 << N)

for s in range(1 << N):
    if s.bit_count() % 2:
        # ペアを作るので、bit が奇数個はあり得ない。
        continue

    for i in range(N):
        if s & (1 << i):
            # 使用済み
            continue
        for j in range(i + 1, N):
            if s & (1 << j):
                # 使用済み
                continue

            ns = s | (1 << i) | (1 << j)

            dp[ns] = max(dp[ns], dp[s] + D[i][j - i - 1])

S = (1 << N) - 1
if N % 2 == 0:
    ans = dp[S]
else:
    # 奇数の時は一人余るので、誰が余るかを考えて答えを出す。
    ans = max(dp[S ^ (1 << i)] for i in range(N))
print(ans)
