N = int(input())
*A, = map(int, input().split())
M = int(input())
*B, = map(int, input().split())
X = int(input())

dp = [0 for _ in range(X+1)]
dp[0] = 1
# b に止まったら動けないので、-inf にしておく
for b in B:
    dp[b] = -float('inf')

for i in range(X):
    if dp[i] < 0:
        continue
    for a in A:
        if i+a > X:
            continue
        dp[i+a] = min(dp[i+a]+dp[i], 1)

print('Yes' if dp[X] > 0 else 'No')
