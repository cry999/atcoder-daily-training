class SegmentTree2D:
    def __init__(self, h: int, w: int):
        self.h = 1
        while self.h < h:
            self.h <<= 1
        self.w = 1
        while self.w < w:
            self.w <<= 1

        self.data = [0] * (4 * self.h * self.w)

    def __id(self, h: int, w: int) -> int:
        return h * 2 * self.w + w

    def set(self, h: int, w: int, x: int):
        self.data[self.__id(h + self.h, w + self.w)] = x

    def build(self):
        for w in range(self.w, 2 * self.w):
            for h in range(self.h - 1, 0, -1):
                self.data[self.__id(h, w)] = max(
                    self.data[self.__id(2 * h + 0, w)],
                    self.data[self.__id(2 * h + 1, w)],
                )
        for h in range(2 * self.h):
            for w in range(self.w - 1, 0, -1):
                self.data[self.__id(h, w)] = max(
                    self.data[self.__id(h, 2 * w + 0)],
                    self.data[self.__id(h, 2 * w + 1)],
                )

    def get(self, h: int, w: int):
        return self.data[self.__id(self.h + h, self.w + w)]

    def update(self, h: int, w: int, x: int):
        h += self.h
        w += self.w
        self.data[self.__id(h, w)] = x

        i = h >> 1
        while i:
            self.data[self.__id(i, w)] = max(
                self.data[self.__id(2 * i + 0, w)],
                self.data[self.__id(2 * i + 1, w)],
            )
            i >>= 1

        while h:
            j = w >> 1
            while j:
                self.data[self.__id(h, j)] = max(
                    self.data[self.__id(h, 2 * j + 0)],
                    self.data[self.__id(h, 2 * j + 1)],
                )
                j >>= 1
            h >>= 1

    def __query(self, h: int, w1: int, w2: int):
        res = 0
        while w1 < w2:
            if w1 & 1:
                res = max(res, self.data[self.__id(h, w1)])
                w1 += 1
            if w2 & 1:
                w2 -= 1
                res = max(res, self.data[self.__id(h, w2)])

            w1 >>= 1
            w2 >>= 1
        return res

    def query(self, h1: int, w1: int, h2: int, w2: int):
        if h1 >= h2 or w1 >= w2:
            return 0

        res = 0
        h1 += self.h
        h2 += self.h
        w1 += self.w
        w2 += self.w

        while h1 < h2:
            if h1 & 1:
                res = max(res, self.__query(h1, w1, w2))
                h1 += 1
            if h2 & 1:
                h2 -= 1
                res = max(res, self.__query(h2, w1, w2))
            h1 >>= 1
            h2 >>= 1

        return res


H, W, h1, w1, h2, w2 = map(int, input().split())
A = [list(map(int, input().split())) for _ in range(H)]

# B: A の累積和を計算する
B = [[0] * (W + 1) for _ in range(H + 1)]
for i in range(H):
    for j in range(W):
        B[i + 1][j + 1] = A[i][j]

for i in range(H + 1):
    for j in range(W):
        B[i][j + 1] += B[i][j]

for j in range(W + 1):
    for i in range(H):
        B[i + 1][j] += B[i][j]

# 白のスタンプは黒のスタンプより大きい分は結果に影響しないので、簡単のために削る。
h2 = min(h1, h2)
w2 = min(w1, w2)

# 白のスタンプの最大値を 2d segtree で管理する
seg = SegmentTree2D(H, W)
for i in range(H - h2 + 1):
    for j in range(W - w2 + 1):
        x = B[i + h2][j + w2] - B[i + h2][j] - B[i][j + w2] + B[i][j]
        seg.update(i, j, x)

ans = 0
for i in range(H - h1 + 1):
    for j in range(W - w1 + 1):
        black = B[i + h1][j + w1] - B[i + h1][j] - B[i][j + w1] + B[i][j]
        white = seg.query(i, j, i + h1 - h2 + 1, j + w1 - w2 + 1)
        ans = max(ans, black - white)

print(ans)
