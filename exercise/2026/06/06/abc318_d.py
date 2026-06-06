N = int(input())
D = [list(map(int, input().split())) for _ in range(N - 1)]

dp = [0] * (1 << N)

for bit in range(1 << N):
    if bit.bit_count() <= 1:
        continue

    for i in range(N):
        if bit & (1 << i) == 0:
            continue

        for j in range(N):
            if i == j:
                continue
            if bit & (1 << j) == 0:
                continue

            prev = bit ^ (1 << i) ^ (1 << j)
            dp[bit] = max(dp[bit], dp[prev] + D[min(i, j)][abs(j - i) - 1])

print(dp[-1])
