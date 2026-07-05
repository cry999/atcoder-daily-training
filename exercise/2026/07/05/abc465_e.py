# >>> atcoder-stat >>>
# started_at  = 2026-07-05T11:02:24+09:00
# solved_at   = 2026-07-05T11:04:58+09:00
# duration_ms = 154092
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
(*N,) = map(int, input())
L = len(N)

MOD = 998244353

# dp[i][S][r][f] :=
#   i 桁目までを決めて
#   利用している数字の集合が S で
#   3 で割ったあまりが r で
#   N より小さいかどうかが f であるような数の個数
dp = [[[[0] * 2 for _ in range(3)] for _ in range(1 << 10)] for _ in range(L + 1)]
dp[0][0][0][0] = 1

for i in range(L):
    n = N[i]
    for s in range(1 << 10):  # i 桁目までの数字の使用状況
        for r in range(3):  # i 桁目までを 3 で割ったあまり
            for less in range(2):  # すでに N 以下が確定か?
                if dp[i][s][r][less] == 0:
                    continue
                # すでに N いかが確定している場合は、なんでも使える
                # そうでない場合は、n 以下
                stop = 9 if less else n
                for d in range(stop + 1):  # i+1 桁目候補
                    ns = s | (1 << d)  # d の使用を追加
                    if ns == 1:  # 0 だけを使うことはあり得ない
                        ns = 0  # 何もないに置き換える
                    nr = (r * 10 + d) % 3
                    nless = less or d < n
                    dp[i + 1][ns][nr][nless] += dp[i][s][r][less]
                    dp[i + 1][ns][nr][nless] %= MOD

ans = 0
for s in range(1 << 10):
    for r in range(3):
        ok = 0
        ok += r == 0
        ok += s & (1 << 3) != 0
        ok += s.bit_count() == 3
        if ok == 1:  # 1 つだけ条件を満たす
            ans += sum(dp[L][s][r])
            ans %= MOD
print(ans - 1)
