N = int(input())
PA = [(0, 0)] + [
    tuple(map(int, input().split())) for _ in range(N)
] + [(N+1, 0)]

# dp[l][r] := l から r までのブロックが残っているときの最高得点
dp = [[0] * (N+2) for _ in range(N+1)]
# dp[l][r] = max(dp[l-1][r] + A[l-1], dp[l][r+1] + A[r+1])
# A[x] = x を P[x] より早く取り除いた場合に得られる得点

for left in range(1, N+1):
    for right in range(N, left-1, -1):
        pl, al = PA[left-1]
        pr, ar = PA[right+1]
        dp[left][right] = max(
            dp[left][right+1] + (ar if left <= pr <= right else 0),
            dp[left-1][right] + (al if left <= pl <= right else 0),
        )

# for row in dp:
#     print(row)
print(max(dp[i][i] for i in range(1, N+1)))
