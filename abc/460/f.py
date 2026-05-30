import sys

sys.setrecursionlimit(10**6)

N = int(input())

# 平衡木を使って、Segment Tree の要領で黒い木のある部分木とその深さの管理をすれば
# 良いのでは？と思ったが、実装できず、また、実装中に、スター型の場合は処理のたびに
# O(N) かかることに気づいて、断念した。最大パスを子供ノードの組み合わせで O(N^2)
# 見ないといけなくて、それをどう管理するのかが時間内にわからずじまい。

g = [[] for _ in range(N)]
for e in range(N - 1):
    a, b = map(int, input().split())
    a -= 1
    b -= 1
    g[a].append(b)
    g[b].append(a)


size = [0 for _ in range(N)]
centroid = []


def dfs_centroid(cur: int, prev: int):
    size[cur] = 1
    mx = 0
    for e in g[cur]:
        if e == prev:
            continue
        size[cur] += dfs_centroid(e, cur)
        mx = max(mx, size[e])
    mx = max(mx, N - size[cur])
    # 一番頂点数の多い枝の数がn/2を超えていないノードは重心として追加
    if mx * 2 <= N:
        centroid.append(cur)

    return size[cur]


dfs_centroid(0, -1)

root = centroid[0]

parent = [i for i in range(N)]
is_black = [True] * N  # 自分が白いか
has_black = [True] * N  # 自分以下のノードに黒いノードがいるか？
deepest_black = [0] * N  # 自分以下のノードのうち、最も深い黒いノードの深さ


def dfs_parent(cur: int, prev: int):
    parent[cur] = prev

    for e in g[cur]:
        if e == prev:
            continue
        deepest_black[cur] = max(deepest_black[cur], dfs_parent(e, cur))
    deepest_black[cur] += 1
    return deepest_black[cur]


dfs_parent(root, -1)


Q = int(input())
for _ in range(Q):
    x = int(input()) - 1

    if is_black[x]:
        is_black[x] = False

        u = x
        while True:
            old_has_black = has_black[u]
            has_black[u] = False
            old_deepest_black = deepest_black[u]
            deepest_black[u] = 0
            for e in g[u]:
                if e == parent[u]:
                    continue
                if has_black[e]:
                    has_black[u] = True
                    break
                deepest_black[u] = max(deepest_black[u], deepest_black[e])
                if deepest_black[u] == old_deepest_black:
                    break

            u = parent[u]
            if u == parent[u]:
                break
    else:
        is_black[x] = True

        u = x
        while True:
            has_black[u] = True
            old_deepest_black = deepest_black[u]
            deepest_black[u] = 0
            for e in g[u]:
                if e == parent[u]:
                    continue
                deepest_black[u] = max(deepest_black[u], deepest_black[e])

            u = parent[u]
            if u == parent[u] or old_deepest_black == deepest_black[u]:
                break

    ans = 0
