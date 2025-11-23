from collections import deque


T = int(input())


def solve():
    n, m = map(int, input().split())
    *x, = map(int, input().split())
    *y, = map(int, input().split())

    # idx_x[n] = n が設定された行番号
    # idx_y[n] = n が設定された列番号
    idx_x, idx_y = [-1] * (n*m+1), [-1] * (n*m+1)

    # 重複チェック
    for i in range(n):
        if idx_x[x[i]] != -1:
            print('No')
            return
        idx_x[x[i]] = i
    for j in range(m):
        if idx_y[y[j]] != -1:
            print('No')
            return
        idx_y[y[j]] = j

    # max_indexes[n] := 設定可能な値の最大値が n であるセルの行列番号
    max_indexes = [[] for _ in range(n*m+1)]
    for i in range(n):
        for j in range(m):
            # 下の q と一緒に利用することで、 min(x[i], y[j]) 以下の値を設定する
            # ためにも利用できる
            max_indexes[min(x[i], y[j])] .append((i, j))

    # a: 条件を満たす行列
    a = [[0] * m for _ in range(n)]
    # q: 現在対象にしているあたいよりも x[i], y[j] ともに大きい (i, j)
    available_indexes = deque()

    for v in range(n*m, 0, -1):
        if idx_x[v] == -1 and idx_y[v] == -1:
            # v が x, y どちらにも含まれない場合
            if not available_indexes:
                print('No')
                return
            # v よりも制限が緩い空いている適当なスペースに突っ込む
            i, j = available_indexes.popleft()
            a[i][j] = v
        elif idx_x[v] == -1 or idx_y[v] == -1:
            # v が x, y のどちらか一方のみに含まれる場合
            if not max_indexes[v]:
                print('No')
                return
            # x[i] = v となる i 行目あるいは、y[j] = v となる j 列目に突っ込む
            i, j = max_indexes[v].pop()
            a[i][j] = v
        else:
            # v が x, y のどちらにも含まれる場合
            # v を設定する箇所は x[i] = y[j] = v を満たす (i, j) だけが許される
            i, j = idx_x[v], idx_y[v]
            a[i][j] = v

        # 残った max_indexes[v] を v 以下の値で利用できるように available_indexes
        # に移動する
        for ri, rj in max_indexes[v]:
            if i == ri and j == rj:
                # 使ったものは continue
                continue
            available_indexes.append((ri, rj))

    print('Yes')
    for row in a:
        print(*row)


for _ in range(T):
    solve()
