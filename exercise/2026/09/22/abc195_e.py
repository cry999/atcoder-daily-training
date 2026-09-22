# >>> atcoder-stat >>>
# started_at  = 2026-09-22T16:19:54+09:00
# solved_at   = 2026-09-22T16:29:04+09:00
# duration_ms = 550368
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
    s, x = int(S[i]), X[i]

    ndp = [False] * 7

    if x == "T":
        # 高橋くんは s か 0 を選んで dp[i] = True となる
        # i に移動できる場合に ndp[j] = True となる。
        for j in range(7):
            ndp[j] = dp[j * 10 % 7] or dp[(j * 10 + s) % 7]
    else:
        # 青木くんのターンで高橋くんの勝ちを考える。
        # この場合は、青木くんが s と 0 のどちらを選んでも dp[i] = True
        # にしか遷移できない場合に高橋くんは必勝で ndp[j] = True となる。
        for j in range(7):
            ndp[j] = dp[j * 10 % 7] and dp[(j * 10 + s) % 7]

    dp[:] = ndp[:]

if dp[0]:
    print("Takahashi")
else:
    print("Aoki")
