import sys

input = sys.stdin.readline


N = int(input())
g = [[] for _ in range(N)]

for i in range(N - 1):
    u, v = map(int, input().split())
    u -= 1
    v -= 1
    g[u].append((v, i))
    g[v].append((u, i))

par = [-1] * N
par_edge = [0] * N
order = [0]

for u in order:
    for v, i in g[u]:
        if v == par[u]:
            continue
        par[v] = u
        par_edge[v] = i
        order.append(v)

sub_size = [1] * N
for u in reversed(order[1:]):
    sub_size[par[u]] += sub_size[u]

offset = 0  # 全体に足す値
cum = [0] * N  # 0 をねとしたとき、v を根とする部分木に対して行う +操作
for u in order[1:]:
    i = par_edge[u]

    if sub_size[u] > N - sub_size[u]:
        # 部分木のサイズが逆より大きい
        cum[u] += i + 1
    else:
        # 部分木のサイズが逆より小さい
        offset += i + 1
        cum[u] -= i + 1

for u in order[1:]:
    cum[u] += cum[par[u]]

print(*[offset + cum[u] for u in range(N)])
