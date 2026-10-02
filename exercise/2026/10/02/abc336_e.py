# >>> atcoder-stat >>>
# started_at  = 2026-10-02T10:02:01+09:00
# solved_at   = 2026-10-02T10:28:56+09:00
# duration_ms = 1615764
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N = input()

ans = 0
for s in range(1, 9 * len(N) + 1):
    # s: 最終的な桁和の値

    # dp[c][r][less]
    # c: 現在の桁和の値
    # r: 現在の値を最終的な桁和の値で割ったあまり
    # less: 現在の値が N より小さいことが確定しているかどうか
    dp = [[[0] * 2 for _ in range(s)] for _ in range(s + 1)]
    dp[0][0][0] = 1
    for i, raw in enumerate(N):
        n = int(raw)
        ndp = [[[0] * 2 for _ in range(s)] for _ in range(s + 1)]
        # 残り全部 9 にしてなんとかなる値が現状の最小値
        c_min = max(0, s - 9 * (len(N) - i))
        # 現在の最大値は、ここまで全部 9 でやってきた場合のみ
        c_max = min(s, 9 * i)

        for c in range(c_min, c_max + 1):
            for r in range(s):
                for less in range(2):
                    if dp[c][r][less] == 0:
                        continue

                    lower = max(0, s - c - 9 * (len(N) - i - 1))
                    upper = min(9 if less else n, s - c)

                    for d in range(lower, upper + 1):
                        nless = less or d < n
                        nc = c + d
                        nr = (r * 10 + d) % s

                        ndp[nc][nr][nless] += dp[c][r][less]

        dp = ndp

    ans += sum(dp[s][0])

print(ans)
