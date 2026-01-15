import sys

sys.setrecursionlimit(10**7)


class SegmentTree:
    def __init__(self, n: int, init: int = 0):
        self.n = 1
        while self.n < n:
            self.n <<= 1
        self.data = [init] * (2 * self.n)
        self.init = init

    def update(self, pos: int, v: int):
        pos = pos + self.n - 1
        self.data[pos] = v

        while pos >= 2:
            pos >>= 1
            self.data[pos] = max(self.data[2 * pos], self.data[2 * pos + 1])

    def query(self, l: int, r: int) -> int:
        """[l, r) の最大値を返す"""
        return self._query(l, r, 1, self.n + 1, 1)

    def _query(self, l: int, r: int, a: int, b: int, u: int) -> int:
        """[a, b) の範囲に対応するセル u が [l, r) を含むならその値を返す。
        含まないなら、二部探索的に探索して対応する値を探す。"""
        if l <= a and b <= r:
            return self.data[u]
        if b <= l or r <= a:  # 交わらない
            return self.init

        m = (a + b) // 2
        return max(
            self._query(l, r, a, m, 2 * u),
            self._query(l, r, m, b, 2 * u + 1),
        )


N = int(input())
(*h,) = map(int, input().split())
(*a,) = map(int, input().split())

t = SegmentTree(N, init=0)

for hi, ai in zip(h, a):
    v = t.query(1, hi) + ai
    t.update(hi, v)

print(t.query(1, N + 1))
