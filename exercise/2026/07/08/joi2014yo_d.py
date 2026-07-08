N = int(input())
S = input()

MOD = 10007


def n(s: str):
    if s == "J":
        return 0
    if s == "O":
        return 1
    return 2


# dp[s] := 出席者の状況が s である時の出席パターン
dp = [0] * (1 << 3)
# 0 日目は J くんだけが出席したことにする。
# (彼が鍵を持っているので)
dp[1 << n("J")] = 1


for i in range(N):
    ndp = [0] * (1 << 3)
    ns = n(S[i])
    for s in range(1 << 3):  # 今日の出席状況
        if s & (1 << ns) == 0:
            continue
        for ys in range(1 << 3):  # 昨日の出席状況
            if s & ys == 0:
                # 鍵を持っている人がいないといけないので、少なくとも1人は
                # 今日も昨日も出席している人がいないといけない。
                continue
            ndp[s] += dp[ys]

    dp = [x % MOD for x in ndp]
print(sum(dp) % MOD)
