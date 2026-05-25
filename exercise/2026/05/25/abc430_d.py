from sortedcontainers import SortedList

N = int(input())
(*X,) = map(int, input().split())

# X[0] で 0 の最も近い距離が更新できるように、仮で X[0] + 1 を初期値にする
q = SortedList([(0, X[0] + 1)])
ans = q[0][1]
for x in X:
    i = q.bisect_left((x, 0))
    if i == len(q):
        x0, d0 = q[-1]

        d = x - x0
        ans += d

        if d0 > d:
            q.pop()
            ans -= d0
            ans += d
            q.add((x0, d))

        q.add((x, d))
    else:
        x1, d1 = q[i]
        x2, d2 = q[i - 1]
        # d1 = q[i][0] - x
        # d2 = x - q[i - 1][0]  # 問題の都合上 i - 1 >= 0 が保証される
        d = min(x1 - x, x - x2)
        ans += d  # x から最も近い距離

        # i の最も近い距離を更新
        if d1 > x1 - x:
            q.pop(i)
            ans -= d1
            ans += x1 - x
            q.add((x1, x1 - x))

        # i-1 の最も近い距離を更新
        if d2 > x - x2:
            q.pop(i - 1)
            ans -= d2
            ans += x - x2
            q.add((x2, x - x2))

        q.add((x, d))

    print(ans)
