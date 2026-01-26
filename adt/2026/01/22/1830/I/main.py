N, M = map(int, input().split())

# pieces_on_node[i] := 頂点 i に置かれている駒のリスト
pieces_on_node = [[i] for i in range(N)]
# node_where_piece_is[i] := 駒 i が置かれている頂点番号。
# 初期位置は駒 i は頂点 i に置かれている。
node_where_piece_is = [i for i in range(N)]

graph: list[set[int]] = [set() for _ in range(N)]
edges: list[tuple[int, int]] = []

for _ in range(M):
    u, v = map(lambda x: int(x) - 1, input().split())
    graph[u].add(v)
    graph[v].add(u)
    edges.append((u, v))


def size(node: int) -> int:
    """頂点に置かれている駒の移動と隣接する頂点の繋ぎ変えを行う必要があるので、
    これらの和を頂点のサイズとして定義する。"""
    return len(graph[node]) + len(pieces_on_node[node])


Q = int(input())
(*X,) = map(lambda x: int(x) - 1, input().split())

ans = M
for q in range(Q):
    x = X[q]
    u, v = edges[x]

    node_u = node_where_piece_is[u]
    node_v = node_where_piece_is[v]
    if node_u == node_v:
        # すでに同じ頂点にあるなら何もしない
        print(ans)
        continue

    size_u, size_v = size(node_u), size(node_v)
    # size の小さい方を移動する方がコストが少なくて済むので、
    # size_u <= size_v で固定する。
    if size_u > size_v:
        node_u, node_v = node_v, node_u

    # node_u に置かれている駒を全て node_v に移動する。
    for piece in pieces_on_node[node_u]:
        pieces_on_node[node_v].append(piece)
        node_where_piece_is[piece] = node_v

    pieces_on_node[node_u].clear()

    # node_u に隣接している頂点で node_v に繋がっていないものを繋ぎなおす。
    for x in graph[node_u]:
        if x == node_v:
            # node_u と node_v をつなぐ辺は縮約されて消える。
            ans -= 1
            graph[node_v].remove(node_u)
            continue

        if x in graph[node_v]:
            # すでに繋がっているなら、node_u と x が繋がっていた辺が消える。
            ans -= 1
        else:
            # 繋がっていないなら繋ぎ直す。辺の数は変わらない。
            graph[node_v].add(x)
            graph[x].add(node_v)

        graph[x].remove(node_u)

    graph[node_u].clear()

    print(ans)
