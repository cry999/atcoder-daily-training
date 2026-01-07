N = int(input())
(*a,) = [tuple(map(int, input().split())) for _ in range(N)]

M = 1 << N

dp = [0] * M

# for i in range(N):
#     for j in range(i + 1, N):
#         dp[(1 << j) | (1 << i)] = a[i][j]
# print(dp)

# O(M^2) だから TLE しそう。
for S in range(M):
    for i in range(N):
        for j in range(i + 1, N):
            if (S & (1 << i)) and (S & (1 << j)):
                dp[S] += a[i][j]

    T = S
    while T > 0:
        T &= S
        if 0 < T < S:
            dp[S] = max(dp[S], dp[T] + dp[T ^ S])
        T -= 1

print(dp[-1])
