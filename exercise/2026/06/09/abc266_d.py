N = int(input())
HOLE = 5
dp = [[-float("inf")] * HOLE for _ in range(10**5 + 1)]
dp[0][0] = 0

last_t = 0
for _ in range(N):
    T, X, A = map(int, input().split())
    # print("[DEBUG]", T, X, A)

    for t in range(last_t, T):
        for x in range(HOLE):
            dp[t + 1][x] = dp[t][x]
            if x - 1 >= 0:
                dp[t + 1][x] = max(dp[t + 1][x], dp[t][x - 1])
            if x + 1 < HOLE:
                dp[t + 1][x] = max(dp[t + 1][x], dp[t][x + 1])

    dp[T][X] += A
    # print("[DEBUG]", dp[: T + 1])

    last_t = T

print(max(dp[last_t]))
# print("[DEBUG]", dp[:last_t])
