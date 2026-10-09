# >>> atcoder-stat >>>
# started_at  = 2026-10-09T08:48:57+09:00
# solved_at   = 2026-10-09T08:59:02+09:00
# duration_ms = 605310
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from atcoder.dsu import DSU

# 考察
# 1. 最終的に求めるのが最小全域木なので、全ての辺を試す必要はない。
# 2. 与えられた S = {A[1], ..., A[k]} は DSU で全て同じクラスターに属する
# 3. この時、A[1] とそれ以外の頂点とをコスト c の辺で結ぶと考えて良い
# 4. なぜなら、パスは関係なく、この頂点が同一クラスタに属し、その辺の最小個数は木になる時なので |S|-1 であるから。
# 5. あとは、この操作を c の昇順で行えば良い。
N, M = map(int, input().split())
edges = []
for _ in range(M):
    _, c = map(int, input().split())
    (*a,) = map(int, input().split())
    edges.append((c, a))

edges.sort(key=lambda x: x[0])  # 配列の比較されると計算量が足りなくなる。
dsu = DSU(N + 1)

ans = 0
for c, a in edges:
    u = a[0]
    for v in a[1:]:
        if dsu.same(u, v):
            continue
        ans += c
        dsu.merge(u, v)

if all(dsu.same(1, i + 1) for i in range(N)):
    print(ans)
else:
    print(-1)
