MOD = 998244353

S = input()
L = len(S)

dp = [[[[0] * 2 for _ in range(3)] for _ in range(1 << 10)] for _ in range(L + 1)]
dp[0][0][0][0] = 1


ans = 0
for i, c in enumerate(S):
    for s in range(1 << 10):  # 先頭 i 桁の 0 ~ 9 の利用状況
        for r in range(3):  # 3 で割ったあまり
            for less in range(2):  # すでに S より小さいかどうか
                cur = dp[i][s][r][less]
                if cur == 0:
                    continue

                # 上位の桁から見ていって
                # 1. すでに S より小さいことが確定 -> 下位の桁はなんでもおける
                # 2. まだ S と同じ -> 下位の桁は S[i] 以下
                max_num = 9 if less else int(c)
                for d in range(max_num + 1):
                    # s == 0 は、まだ有効な数字を一つも置いていない状態
                    # この状態で d == 0 を置く場合、それは leading zero なので
                    # 数字 0 を「使った」とはみなさず、集合は空のままにする。
                    #
                    # 例: N が 4 桁のとき、数 7 は 0007 として扱うが、
                    # 使った数字集合は {0, 7} ではなく {7} にしたい。
                    if s == 0 and d == 0:
                        ns = 0
                    else:
                        ns = s | (1 << d)

                    nr = (r * 10 + d) % 3
                    nless = less or d < int(c)
                    dp[i + 1][ns][nr][nless] += cur
                    dp[i + 1][ns][nr][nless] %= MOD

for s in range(1, 1 << 10):
    for r in range(3):
        for less in range(2):
            ok = 0
            ok += s.bit_count() == 3
            ok += s & (1 << 3) != 0
            ok += r == 0
            if ok == 1:
                ans += dp[L][s][r][less]
                ans %= MOD
print(ans)
