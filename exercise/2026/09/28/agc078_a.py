# >>> atcoder-stat >>>
# started_at  = 2026-09-28T03:53:50+09:00
# solved_at   = 2026-09-28T09:14:36+09:00
# duration_ms = 19246145
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from atcoder.mincostflow import MCFGraph

N = int(input())
S = input()
T = input()


W = N + 1
M = 2 * W * W


def node(i: int, j: int):
    return i * W + j


def support(u: int):
    return u + W * W


def get_index_of_abc(s: str) -> tuple[list[int], list[int], list[int]]:
    # 右から i 番目の A の s 上での位置
    a_on_s: list[int] = []
    # 左から i 番目の C の s 上での位置
    c_on_s: list[int] = []
    # s 上の B の位置 (B は index はいらない)
    b_on_s: list[int] = []

    for i in range(3 * N):
        if s[i] == "A":
            a_on_s.append(i)
        elif s[i] == "C":
            c_on_s.append(i)
        else:
            # na: この B より右にある A の数
            na = N - len(a_on_s)
            # nc: この B より左にある C の数
            nc = len(c_on_s)
            # B を (na, nc) に置く。グラフの頂点番号としては na*N + nc として扱う
            b_on_s.append(node(na, nc))

    a_on_s.reverse()  # 右から i 番目の A の位置を求めるために reverse する

    return a_on_s, b_on_s, c_on_s


a_on_s, b_on_s, c_on_s = get_index_of_abc(S)
a_on_t, b_on_t, c_on_t = get_index_of_abc(T)


source = M
sink = M + 1
g = MCFGraph(M + 2)

for x in range(W):
    for y in range(W):
        u = node(x, y)
        if x > 0:
            g.add_edge(u, node(x - 1, y), N, 1)
        if y > 0:
            g.add_edge(u, node(x, y - 1), N, 1)

fixed_cost = 0  # A と C の転倒数
for x in range(1, W):
    for y in range(1, W):
        if a_on_s[x - 1] < c_on_s[y - 1] and c_on_t[y - 1] < a_on_t[x - 1]:
            # AC を CA にすることはできない。
            print(-1)
            exit()

        if c_on_s[y - 1] < a_on_s[x - 1] and a_on_t[x - 1] < c_on_t[y - 1]:
            fixed_cost += 1

            # CA を AC にする場合は、追加で辺を張る
            p = node(x, y)  # 左下に向かって u に入る
            q = node(x - 1, y)  # 下に向かって u に入る
            r = node(x, y - 1)  # 左に向かって u に入る
            u = node(x - 1, y - 1)
            v = support(u)

            g.add_edge(p, v, N, 0)
            g.add_edge(q, v, N, 0)
            g.add_edge(r, v, N, 0)
            g.add_edge(v, u, 1, 0)


# S 上の B の位置に source から容量 1 / コスト 0 の辺を張る。
for b in b_on_s:
    g.add_edge(source, b, 1, 0)

# T 上の B の位置に sink への容量 1 / コスト 0 の辺を張る。
for b in b_on_t:
    g.add_edge(b, sink, 1, 0)

flow, cost = g.flow(source, sink)
if flow < N:
    print(-1)
else:
    print(cost + fixed_cost)
