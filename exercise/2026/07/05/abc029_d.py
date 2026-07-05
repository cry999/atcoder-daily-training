# >>> atcoder-stat >>>
# started_at  = 2026-07-05T10:17:38+09:00
# solved_at   = 2026-07-05T10:52:34+09:00
# duration_ms = 2096253
# target_ms   = 900000
# ac          = true
# editorial   = true
# knowledge   = 2
# translation = 1
# complexity  = 3
# impl        = 1
# verify      = 2
# <<< atcoder-stat <<<
(*N,) = map(int, input())
L = len(N)

# dp[i][less] := i 桁目まで見たときに、N 以下が確定しているかどうかが less であるときの、
# (そういった数の個数, 1 の個数の合計)
dp = [[[0, 0] for _ in range(2)] for _ in range(L + 1)]
dp[0][0][0] = 1

for i in range(L):
    n = N[i]
    for less in range(2):
        cnt, ones = dp[i][less]
        if cnt == 0:
            continue
        print(f"[DEBUG] {i=} {less=} {cnt=} {ones=}")
        # すでに N 以下が確定している場合は、なんでも使える
        # そうでない場合は、n 以下
        stop = 9 if less else n
        for d in range(stop + 1):
            print(f"[DEBUG] {i=} {less=} {d=}")
            nless = less or d < n
            dp[i + 1][nless][0] += cnt
            dp[i + 1][nless][1] += ones

            if d == 1:
                dp[i + 1][nless][1] += cnt

print(dp[L][0][1] + dp[L][1][1])
