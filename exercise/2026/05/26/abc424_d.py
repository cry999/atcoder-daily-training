T = int(input())


def conv(s: str) -> int:
    ret = 0
    for c in s:
        ret <<= 1
        if c == "#":
            ret += 1
    return ret


for _ in range(T):
    H, W = map(int, input().split())
    S = [conv(input()) for _ in range(H)]

    dp = [[float("inf")] * (1 << W) for _ in range(H + 1)]
    for i in range(1 << W):
        dp[0][i] = 0

    for h in range(H):
        for s in range(1 << W):
            if s & S[h] != s:
                # S[h] で白く塗られたところを白くすることはできない。
                continue
            # 白く塗る箇所
            op = (s ^ S[h]).bit_count()
            for t in range(1 << W):
                # t: 前の行の塗り状態
                # s & t で 11 の箇所がある => 条件を満たす塗り方ではない
                n = s & t
                ok = True
                while n:
                    if n & 0b11 == 0b11:
                        ok = False
                        break
                    n >>= 1
                if not ok:
                    continue
                dp[h + 1][s] = min(dp[h + 1][s], dp[h][t] + op)

    ans = min(dp[H])
    print(ans)
