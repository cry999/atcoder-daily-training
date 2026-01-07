N, K = map(int, input().split())
(*a,) = map(int, input().split())

dp = [False] * (K + 1)

for k in range(1, K + 1):
    dp[k] = any(k - v >= 0 and not dp[k - v] for v in a)

# print(dp)
if dp[K]:
    print("First")
else:
    print("Second")
