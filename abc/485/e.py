import sys

N, M = map(int, input().split())
g: list[list[tuple[int, int]]] = [[] for _ in range(N)]
for _ in range(M):
    u, v, c = map(int, input().split())
    u -= 1
    v -= 1
    g[u].append((v, c))

INF = 10**18

# (node, color, dist)
q = [(0, -1, 0)]
first = [-1] * N  # 最初に到達した時の辺の番号
is_second = [False] * N  # 最初に到達した時の辺番号とは別の番号でも到達したか
for u, c, d in q:
    # print(f"[DEBUG] {u=} {c=} {d=} {dist=}")
    for v, c2 in g[u]:
        if c == first[u]:
            # 1st time: c 以外の辺だけ調べる
            if c == c2:
                continue
        else:
            # 2nd time: 1 回目に通れなかった辺だけ調べる
            if c2 != first[u]:
                continue
        if first[v] == -1:
            first[v] = c2
        elif c2 != first[v] and not is_second[v]:
            is_second[v] = True
        else:
            continue
        if v == N - 1:
            print(d + 1)
            sys.exit()
        q.append((v, c2, d + 1))
print(-1)
