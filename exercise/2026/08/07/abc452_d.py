# >>> atcoder-stat >>>
# started_at  = 2026-08-07T05:39:13+09:00
# solved_at   = 2026-08-07T05:57:17+09:00
# duration_ms = 1084536
# target_ms   = 900000
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 1
# complexity  = 3
# impl        = 1
# verify      = 3
# <<< atcoder-stat <<<
S = input()
T = input()
N, M = len(S), len(T)

dp = [0] * (M + 1)
contain = 0
for c in S:
    ndp = [0] * (M + 1)

    # c 1文字だけからなる、新しい部分文字列
    if c == T[0]:
        # T[0] と一致するなら一致する文字数は 1 なので ndp[1] に追加
        ndp[1] += 1
    else:
        # T[0] と一致しないなら一致する文字数は 0 なので ndp[0] に追加
        ndp[0] += 1

    # 既存の部分文字列に c を追加する場合
    for j in range(M + 1):
        if j == M:
            # 既に T と一致している場合は、c を追加しても T と一致する部分文字列の数は変わらない
            ndp[j] += dp[j]
        elif c == T[j]:
            # c が T[j] と一致する場合は、一致する文字数が 1 増えるので ndp[j + 1] に追加
            ndp[j + 1] += dp[j]
        else:
            # c が T[j] と一致しない場合は、一致する文字数は変わらないので ndp[j] に追加
            ndp[j] += dp[j]

    contain += ndp[M]
    dp = ndp

print(N * (N + 1) // 2 - contain)
