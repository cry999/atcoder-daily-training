# >>> atcoder-stat >>>
# started_at  = 2026-10-09T09:08:53+09:00
# <<< atcoder-stat <<<
N, Q = map(int, input().split())
g = [[] for _ in range(N)]

for i in range(N - 1):
    a, b, c = map(int, input().split())
    a -= 1
    b -= 1
    g[a].append((b, c, i))
    g[b].append((a, c, i))


# 考察
# 1. 最初の状態は MST
# 2. クエリの辺を追加するかどうか。
# 3. 与えられた時に必要ないなら、その後も必要にはならない。
# なぜなら、u, v を繋ぐのにもっと効率的な繋ぎ方があるということだから
# 4. クエリの辺を使いする場合. a: すでに (u, v) を繋ぐ辺が採用されている or b: (u, v) を繋ぐ辺を追加するとループができる
# 4.a. 置き換えるだけ
# 4.b. ループの中で最も重い辺を削除する。これは LCA を利用する？

# 初期の木に対する LCA と経路上の最大辺をダブリングで求める。
# 辺を交換した後は、この前処理をそのまま使えないことに注意。
L = N.bit_length()
par = [[0] * N for _ in range(L)]
# mx[k][v]: v から 2**k 個上の祖先までの (最大重み, 辺 ID)
# 重みは正なので、辺がない場合は (0, -1) とする。
mx = [[(0, -1)] * N for _ in range(L)]
dep = [-1] * N
dep[0] = 0
stack = [0]
while stack:
    v = stack.pop()
    for u, w, i in g[v]:
        if dep[u] != -1:
            continue
        dep[u] = dep[v] + 1
        par[0][u] = v
        mx[0][u] = (w, i)
        stack.append(u)

for k in range(1, L):
    for v in range(N):
        p = par[k - 1][v]
        par[k][v] = par[k - 1][p]
        mx[k][v] = max(mx[k - 1][v], mx[k - 1][p])


def lca(u, v):
    # 頂点番号は 0-indexed。
    if dep[u] < dep[v]:
        u, v = v, u
    d = dep[u] - dep[v]
    for k in range(L):
        if d >> k & 1:
            u = par[k][u]
    if u == v:
        return u
    for k in range(L - 1, -1, -1):
        if par[k][u] != par[k][v]:
            u = par[k][u]
            v = par[k][v]
    return par[0][u]


def max_edge(u, v):
    # 同じ頂点なら (0, -1)。同じ最大重みの辺が複数あれば ID 最大を返す。
    a = lca(u, v)
    res = (0, -1)
    for x in (u, v):
        d = dep[x] - dep[a]
        for k in range(L):
            if d >> k & 1:
                res = max(res, mx[k][x])
                x = par[k][x]
    return res


# クエリ (u, v, w) では max_edge(u - 1, v - 1) で交換候補を探せる。
# TODO: 辺の交換に対応する仕組みと、各クエリの MST 重みの出力。
