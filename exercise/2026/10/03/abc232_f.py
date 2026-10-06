# >>> atcoder-stat >>>
# started_at  = 2026-10-03T11:07:58+09:00
# solved_at   = 2026-10-03T11:14:56+09:00
# duration_ms = 418969
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, X, Y = map(int, input().split())
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())

# 考察
# 1. X と Y は独立した操作
# 2. Y の並び替えが終わってから X で差分を埋めれば良い
# 3. Y の並び替えを bit DP で行う。
# 4. 管理するのは、A の要素のうち B の 1 ~ |S| までとマッチング済みの集合
# 5. S に対して i が新たに追加される時、S にまだ追加されていない i 未満の数が移動回数になる
# 6. したがって、dp[S | i] = dp[S] + abs(B[|S|] - A[i]) * X + less * Y


INF = 10**18
dp = [INF] * (1 << N)
dp[0] = 0

for s in range(1 << N):
    less = 0
    size = s.bit_count()
    for i in range(N):
        if s & (1 << i):
            continue
        ns = s | (1 << i)
        dp[ns] = min(dp[ns], dp[s] + abs(B[size] - A[i]) * X + less * Y)
        less += 1

print(dp[-1])
