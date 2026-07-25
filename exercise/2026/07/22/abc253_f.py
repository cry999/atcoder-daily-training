# >>> atcoder-stat >>>
# started_at  = 2026-07-22T06:39:34+09:00
# solved_at   = 2026-07-22T07:09:24+09:00
# duration_ms = 1790901
# ac          = true
# editorial   = true
# knowledge   = 2
# translation = 2
# complexity  = 2
# impl        = 1
# verify      = 2
# <<< atcoder-stat <<<
from atcoder.lazysegtree import LazySegTree

INF = float("inf")

N, M, Q = map(int, input().split())
queries = [tuple(map(int, input().split())) for _ in range(Q)]

# attached[i] := タイプ 2 クエリ i を直前の行更新としてもつタイプ 3 クエリの情報
attached = [[] for _ in range(Q)]

# 各行に対する直前のタイプ 2 クエリ番号
last_row_update = [-1] * (N + 1)

for i, (q, *args) in enumerate(queries):
    if q == 2:
        r, _ = args
        last_row_update[r] = i
    elif q == 3:
        r, c = args
        if last_row_update[r] != -1:
            attached[last_row_update[r]].append((i, c))

lst = LazySegTree(
    op=lambda x, y: max(x, y),
    e=-INF,
    mapping=lambda f, v: f + v,
    composition=lambda f, g: f + g,
    id_=0,
    v=[0] * (M + 1),
)


ans = [0] * Q
for i, (q, *args) in enumerate(queries):
    if q == 1:
        l, r, x = args
        lst.apply(l, r + 1, x)
    elif q == 2:
        _, x = args
        # このタイプ 2 を直前の行更新としてもつタイプ 3 だけを処理する
        for qi, c in attached[i]:
            ans[qi] = x - lst.get(c)
    else:
        r, c = args
        ans[i] += lst.get(c)
        print(ans[i])
