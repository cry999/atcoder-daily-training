# >>> atcoder-stat >>>
# started_at  = 2026-09-30T10:26:17+09:00
# solved_at   = 2026-09-30T10:58:43+09:00
# duration_ms = 1946079
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 1
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
N, X, Y = map(int, input().split())
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())

INF = 10**18
# dp[S] := i ∈ S となる i について、A[i] を B[1] ... B[|S|] と対応させ終わった時の最小コスト
dp = [INF] * (1 << N)
dp[0] = 0
for s in range(1 << N):
    j = s.bit_count()  # |S|
    # less_cnt: 注目している i より小さい添え字で S に含まれていないものの個数
    # この個数が、A[i] を B[j] にマッチさせるために移動させないといけない個数
    less_cnt = 0
    for i in range(N):
        # A[i] と B[|S|] を対応させる
        if s & (1 << i):
            continue
        ns = s | (1 << i)
        dp[ns] = min(dp[ns], dp[s] + abs(A[i] - B[j]) * X + less_cnt * Y)

        less_cnt += 1
print(dp[-1])
