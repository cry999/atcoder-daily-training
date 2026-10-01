# >>> atcoder-stat >>>
# started_at  = 2026-10-01T08:27:44+09:00
# solved_at   = 2026-10-01T08:37:25+09:00
# duration_ms = 581866
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
# 1. 操作 X と操作 Y は独立
# 2. 操作 Y を全部行って、A の並べ替え後の位置を完了させてから操作 X による差分計算をすれば良い
# 3. 操作 Y の結果をどう列挙するか？全列挙は N! = 18! で全く間に合わない
# 4. bit DP で集合 S を管理する。S = {A の添え字で、B の先頭から |S| 番目までとマッチング済みの集合}
# 5. S の中の並びは考える必要はない。S に追加する次の i は常に S の末尾に追加すると考えても、問題ない。

INF = 10**18
dp = [INF] * (1 << N)
dp[0] = 0

for s in range(1 << N):
    less = 0
    size = s.bit_count()
    for i in range(N):
        if s & (1 << i):
            # すでに含まれている
            continue
        # A[i] を S の末尾に追加する場合の移動コストは、s に含まれない A[j] のうち
        # j < i を満たすものの個数。したがって less をカウントしている。
        cost = abs(A[i] - B[size]) * X + less * Y
        nxt = s | (1 << i)

        dp[nxt] = min(dp[nxt], dp[s] + cost)

        less += 1

print(dp[-1])
