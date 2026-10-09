# >>> atcoder-stat >>>
# started_at  = 2026-10-09T08:59:12+09:00
# solved_at   = 2026-10-09T09:08:40+09:00
# duration_ms = 568860
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from atcoder.dsu import DSU

N, M = map(int, input().split())
(*A,) = map(int, input().split())

# 考察
# 1. 順番は関係あるか？
# M で割ったあまり出なければ、y は最大の数字を選んで、そのほかを x に割り当てれば良い。
# なので、順番は関係ない。
# しかし、M で割ったあまりの場合はどうだ？
# 2. N が小さいので、N^2 は全然余裕。
# 全てのボールの組み合わせ (x, y) に対して (x^y + y^x) % M を計算できる。
# これを消化する順番を考えないといけない？
# 3. 大きい順に消化していくという貪欲法でいけるか？


edges = []
for i in range(N):
    for j in range(i + 1, N):
        x, y = A[i], A[j]
        score = (pow(x, y, M) + pow(y, x, M)) % M
        edges.append((score, i, j))

edges.sort(reverse=True)
dsu = DSU(N)
ans = 0
for score, i, j in edges:
    if dsu.same(i, j):
        continue
    dsu.merge(i, j)
    ans += score
print(ans)
