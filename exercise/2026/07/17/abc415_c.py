# >>> atcoder-stat >>>
# started_at  = 2026-07-17T18:45:37+09:00
# solved_at   = 2026-07-17T18:52:00+09:00
# duration_ms = 383943
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
T = int(input())

for _ in range(T):
    N = int(input())
    S = input()

    dp = [0] * (1 << N)
    dp[0] = 1

    for s in range(1 << N):
        for i in range(N):
            if s & (1 << i):
                # すでに混ぜてある
                continue
            ns = s | (1 << i)
            if S[ns - 1] == "1":
                # 混ぜた状態が危険な状態なら回避
                continue
            dp[ns] += dp[s]

    ALL = (1 << N) - 1
    print("Yes" if dp[ALL] else "No")
