N, C = map(int, input().split())
(*h,) = map(int, input().split())


class LiChao:
    def __init__(self, xs: list[int]) -> None:
        self.xs = xs
        self.n = len(xs)
        self.m = [0] * (4 * self.n)
        self.b = [float("inf")] * (4 * self.n)
        self.has = [False] * (4 * self.n)

    @staticmethod
    def f(m: float, b: float, x: int) -> float:
        return m * x + b

    def add_line(self, m: float, b: float) -> None:
        self._add_line(1, 0, self.n - 1, m, b)

    def _add_line(self, idx: int, l: int, r: int, m: float, b: float) -> None:
        if not self.has[idx]:
            self.has[idx] = True
            self.m[idx], self.b[idx] = m, b
            return

        mid = (l + r) // 2
        xl, xm, xr = self.xs[l], self.xs[mid], self.xs[r]
        cm, cb = self.m[idx], self.b[idx]

        # midで良い方を残す（min）
        if self.f(m, b, xm) < self.f(cm, cb, xm):
            self.m[idx], self.b[idx], m, b = m, b, cm, cb
            cm, cb = self.m[idx], self.b[idx]

        if l == r:
            return

        if self.f(m, b, xl) < self.f(cm, cb, xl):
            self._add_line(idx * 2, l, mid, m, b)
        elif self.f(m, b, xr) < self.f(cm, cb, xr):
            self._add_line(idx * 2 + 1, mid + 1, r, m, b)

    def query(self, x: int) -> float:
        pos = self._lower_bound(x)
        return self._query(1, 0, self.n - 1, pos)

    def _query(self, idx: int, l: int, r: int, pos: int) -> float:
        res = float("inf")
        if self.has[idx]:
            res = min(res, self.f(self.m[idx], self.b[idx], self.xs[pos]))
        if l == r:
            return res
        mid = (l + r) // 2
        if pos <= mid:
            return min(res, self._query(idx * 2, l, mid, pos))
        else:
            return min(res, self._query(idx * 2 + 1, mid + 1, r, pos))

    def _lower_bound(self, x: int) -> int:
        lo, hi = 0, len(self.xs)
        while lo < hi:
            mid = (lo + hi) // 2
            if self.xs[mid] < x:
                lo = mid + 1
            else:
                hi = mid
        return lo


lc = LiChao(h)

dp = [0] * N
lc.add_line(-2 * h[0], dp[0] + h[0] * h[0])  # = h0^2

for i in range(1, N):
    best = lc.query(h[i])
    dp[i] = h[i] * h[i] + C + best
    lc.add_line(-2 * h[i], dp[i] + h[i] * h[i])

print(dp[-1])
