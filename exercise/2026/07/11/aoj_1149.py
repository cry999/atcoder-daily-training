class FenwickTree:
    def __init__(self, n: int):
        self.n = n
        self.data = [0] * (n + 1)

    def add(self, i: int, x: int):
        i += 1

        while i <= self.n:
            self.data[i] += x
            i += i & -i

    def kth(self, k: int):
        """
        累積和が初めて k 以上になる 0-indexed の位置を返す。
        k は 1-indexed。
        """
        i = 0
        bit = 1 << (self.n.bit_length() - 1)

        while bit:
            ni = i + bit

            if ni <= self.n and self.data[ni] < k:
                k -= self.data[ni]
                i = ni

            bit >>= 1

        return i


while True:
    N, W, D = map(int, input().split())
    if N == W == D == 0:
        break
    cakes = [(W, D)]
    indexes = FenwickTree(2 * N + 1)
    indexes.add(0, 1)
    active = [True]

    for _ in range(N):
        p, s = map(int, input().split())

        i = indexes.kth(p)
        indexes.add(i, -1)
        active[i] = False
        w, d = cakes[i]

        # 1 周に収める
        s %= 2 * (w + d)
        if s < w:
            # 上辺に切れ目を入れる
            p1, p2 = (s, d), (w - s, d)
        elif s < w + d:
            # 右辺に切れ目を入れる
            d1 = s - w
            p1, p2 = (w, d1), (w, d - d1)
        elif s < 2 * w + d:
            # 下辺に切れ目を入れる
            w1 = s - (w + d)
            p1, p2 = (w1, d), (w - w1, d)
        else:
            # 左辺に切れ目を入れる
            d1 = s - (2 * w + d)
            p1, p2 = (w, d1), (w, d - d1)

        if p1[0] * p1[1] > p2[0] * p2[1]:
            p1, p2 = p2, p1

        indexes.add(len(cakes), 1)
        cakes.append(p1)
        active.append(True)

        indexes.add(len(cakes), 1)
        cakes.append(p2)
        active.append(True)

    print(*sorted(w * d for i, (w, d) in enumerate(cakes) if active[i]))
