N, T, M = map(int, input().split())

# hate[i] := i 番目の人が嫌いな人の集合 (嫌いなら hate[i] & j != 0)
hate = [0] * N
for _ in range(M):
    a, b = map(lambda x: int(x) - 1, input().split())

    hate[a] |= 1 << b
    hate[b] |= 1 << a

# possible[S] := S に含まれる人で構成されるチームがありえるか
possible = [False] * (1 << N)
for s in range(1 << N):
    # s に含まれる人の嫌いな人を集める
    hates = 0
    for i in range(N):
        if s & (1 << i):
            hates |= hate[i]

    # s と hates に共通部分があるなら嫌いな人同士が含まれるので NG
    # 共通部分がないなら OK
    possible[s] = (s & hates) == 0

# dp[S][t] := S に含まれる人で構成されるチームをちょうど t チームに分ける方法
dp = [[0] * (T + 1) for _ in range(1 << N)]
dp[0][0] = 1

for cur_s in range(1 << N):
    # nxt_s は cur_s に含まれない最小メンバーを必ず含む
    nxt_s = cur_s + 1 | cur_s
    while nxt_s < (1 << N):
        # nxt_s から cur_s を除くと新規チームになる
        new_team = nxt_s ^ cur_s
        if possible[new_team]:
            for t in range(T):
                dp[nxt_s][t + 1] += dp[cur_s][t]

        nxt_s = (nxt_s + 1) | (cur_s + 1) | cur_s

print(dp[(1 << N) - 1][T])
