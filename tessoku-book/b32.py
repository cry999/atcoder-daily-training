N, K = map(int, input().split())
A = list(map(int, input().split()))

dp = [False] * (N + 1)
for i in range(1, N + 1):
    for a in A:
        if i - a < 0 or dp[i-a]:
            continue
        dp[i] = True
        break

# print(dp)
print('First' if dp[N] else 'Second')
