T = int(input())

for _ in range(T):
    N, H = map(int, input().split())
    # pt, pl, pu: 一個前の通過点での時間、最低到達点、最高到達点
    pt, pl, pu = 0, H, H
    available = True
    for _ in range(N):
        t, l, u = map(int, input().split())
        if not available:
            continue
        diff = t-pt
        nl = min(
            # pl からの最低到達点: pl から diff 下がる。
            # pl と diff の偶奇が一致するなら 0 が最低、一致しないなら 1 が最低。
            max((pl-diff) % 2, pl-diff),
            # pu からの最低到達点: pu から diff 下がる。
            max((pu-diff) % 2, pu-diff),
        )
        nu = max(pl+diff, pu+diff)

        # [nl, nu] と [l, u] が交差するなら移動可能。
        # 交差しないなら不可能なのでこの時点で終了。
        if nu < l or u < nl:
            # 交差しない
            available = False
        # 交差するなら pt, pl, pu を更新して次に行く。
        pt, pl, pu = t, max(l, nl), min(u, nu)

    print('YNeos'[not available::2])
