# >>> atcoder-stat >>>
# started_at  = 2026-09-10T10:34:34+09:00
# solved_at   = 2026-09-10T10:40:13+09:00
# duration_ms = 339565
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())
S = input()
X = input()

dp = [False] * 7
dp[0] = True

for i in range(N - 1, -1, -1):
    s = int(S[i])
    ndp = [False] * 7
    if X[i] == "T":
        # 高橋君のターンは、各 j について、S[i] か 0 のどちらかで遷移したら
        # 次のターンの確定しているなら今回のターンを True にする
        for r in range(7):
            ndp[r] = dp[(r * 10 + s) % 7] or dp[r * 10 % 7]
    else:
        # 青木君のターンは、各 j について、S[i] と 0 のどちらに遷移しても高橋君が
        # 勝ち確なら高橋君の勝ち確
        for r in range(7):
            ndp[r] = dp[(r * 10 + s) % 7] and dp[r * 10 % 7]

    dp[:] = ndp[:]

print("Takahashi" if dp[0] else "Aoki")
