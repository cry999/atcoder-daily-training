# >>> atcoder-stat >>>
# started_at  = 2026-09-09T15:34:12+09:00
# solved_at   = 2026-09-09T16:01:45+09:00
# duration_ms = 1653738
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 1
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())
S = input()
X = input()

# True: Takahashi の勝ち, False: Aoki の勝ち
dp = [False] * 7
dp[0] = True


for i in range(N - 1, -1, -1):
    s = int(S[i])
    ndp = [False] * 7
    if X[i] == "T":
        # Takahashi のターン
        # dp[i] = True となるように S[i] か 0 を選択する。
        # そのために True になっていて欲しい箇所を ndp に設定する。
        for j in range(7):
            ndp[j] = dp[10 * j % 7] or dp[(10 * j + s) % 7]
    else:
        # Aoki のターン
        # dp[i] = False となるように S[i] か 0 を選択する。
        for j in range(7):
            # Aoki 君が 0 を選んでも S[i] を選んでも Takahashi 君が
            # 勝てるので、j が選ばれていると Takahshi 君は勝てる
            ndp[j] = dp[10 * j % 7] and dp[(10 * j + s) % 7]

    dp[:] = ndp[:]
    print(f"[DEBUG] {dp=}")
print("Takahashi" if dp[0] else "Aoki")
