N, A, B = map(int, input().split())
# dp[i] := i 個残っている手番がきたらときの勝ち負け
dp = [False] * (N+1)

for i in range(1, N+1):
    dp[i] = dp[i] or (i-A >= 0 and not dp[i-A]) or (i-B >= 0 and not dp[i-B])
print('First' if dp[N] else 'Second')
