MOD = 10**9 + 7


N = int(input())
s = input()

# dp[i][n]: i 番目までを s にしたがって並べた上で末尾が n である場合の数
dp = [[0] * N for _ in range(N)]
dp[0][0] = 1
ss = [0] * (N + 1)
for i in range(N):
    ss[i + 1] = ss[i] + dp[0][i]


for i in range(1, N):
    c = s[i - 1]
    if c == "<":
        for k in range(1, i + 1):
            dp[i][k] = ss[k] - ss[0]
    else:
        for k in range(i + 1):
            dp[i][k] = ss[i] - ss[k]
    # print(f"  before dp[{i}]={dp[i]}")
    for j in range(N):
        ss[j + 1] = (ss[j] + dp[i][j]) % MOD
    # print(f"  after  {ss=}")

print(ss[-1])
