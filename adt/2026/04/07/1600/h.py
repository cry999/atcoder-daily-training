N = int(input())
S = input()

NUM_CONTEST = 10
MOD = 998244353

# dp[i][S][j] :=
# コンテストの i 回目まで出場するかどうかを決めていて、
# 出場したコンテストの集合が S かつ
# 最後に出場したコンテストが j である
# 出場方法の総数。
dp = [[[0] * NUM_CONTEST for _ in range(1 << NUM_CONTEST)] for _ in range(2)]
dp[0][0][0] = 1


for i in range(N):
    x = ord(S[i]) - ord("A")
    i %= 2

    for state in range(1 << NUM_CONTEST):
        # S[i] に出場しない場合
        for last in range(NUM_CONTEST):
            dp[(i + 1) % 2][state][last] = dp[i][state][last]

    for state in range(1 << NUM_CONTEST):
        # S[i] に出場する場合
        if state & (1 << x):
            # すでに同一種類のコンテストに出場済みの時は、前回が同一コンテストの
            # 時だけ出場可能
            dp[(i + 1) % 2][state][x] += dp[i][state][x]
            dp[(i + 1) % 2][state][x] %= MOD
        else:
            # 新規出場の場合、とりあえず出場して良い。
            dp[(i + 1) % 2][state | (1 << x)][x] += sum(dp[i][state])
            dp[(i + 1) % 2][state | (1 << x)][x] %= MOD

ans = 0
# state = 0 (何も出場しない) を除外
for state in range(1, 1 << NUM_CONTEST):
    ans += sum(dp[N % 2][state])
    ans %= MOD

print(ans)
