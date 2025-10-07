N, K = map(int, input().split())
AB = [tuple(map(int, input().split())) for _ in range(N)]

# dp[A][B]: 参加者の体力の最小値が A, 気力の最小値が B の場合の最大参加人数
dp = [[0] * (100-K+1) for _ in range(100-K+1)]

for a in range(100-K+1):
    for b in range(100-K+1):
        for A, B in AB:
            if a <= A <= a+K and b <= B <= b+K:
                dp[a][b] += 1
print(max(map(max, dp)))
