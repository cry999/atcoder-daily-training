from sortedcontainers import SortedDict

T = int(input())

for _ in range(T):
    N, X = map(int, input().split())
    A = list(map(int, input().split()))

    # 半開区間 [0, X + 1) が 1 個
    targets = SortedDict()
    targets[X + 1] = 1

    for a in A:
        # x <= a なら x % a = x なので更新不要
        while targets and targets.peekitem(-1)[0] > a:
            x, n = targets.popitem(-1)

            q, r = divmod(x, a)

            # [0, a) が q 個できる
            targets[a] = targets.get(a, 0) + n * q

            # [0, r) が 1 個できる
            if r > 0:
                targets[r] = targets.get(r, 0) + n

    # 各区間が 0 を一つずつ表す
    # 全体として値 0 は除外する
    print(sum(targets.values()) - 1)
