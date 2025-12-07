from collections import deque


N, M = map(int, input().split())

g = [[] for _ in range(N+1)]

for _ in range(M):
    X, Y = map(int, input().split())
    # 黒に到達できる、という状態は逆向きに伝搬するので
    # 辺を逆向きに張る。
    g[Y].append(X)

is_black = [False] * (N+1)

Q = int(input())
for _ in range(Q):
    q, v = map(int, input().split())

    if q == 1:
        # 頂点 v を黒にして、そこから連結する頂点も黒く塗っていく。
        if is_black[v]:
            # すでに黒いなら何もしない
            continue
        is_black[v] = True
        queue = deque([v])
        while queue:
            u = queue.popleft()
            for to in g[u]:
                if is_black[to]:
                    continue
                is_black[to] = True
                queue.append(to)
    else:  # q == 2
        print('Yes' if is_black[v] else 'No')
