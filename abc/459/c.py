class FenwickTree:
    """Reference: https://en.wikipedia.org/wiki/Fenwick_tree"""

    def __init__(self, n: int = 0) -> None:
        self._n = n
        self.data = [0] * n

    def add(self, p: int, x: int) -> None:
        assert 0 <= p < self._n

        p += 1
        while p <= self._n:
            self.data[p - 1] += x
            p += p & -p

    def sum(self, left: int, right: int) -> int:
        assert 0 <= left <= right <= self._n

        return self._sum(right) - self._sum(left)

    def _sum(self, r: int) -> int:
        s = 0
        while r > 0:
            s += self.data[r - 1]
            r -= r & -r

        return s


N, Q = map(int, input().split())
base = 0
hights = [0] * N
num = [0] * (Q + 2)  # num[h]: 高さが h 以上のマスの個数
num[0] = N

bit = FenwickTree(Q + 1)
bit.add(0, N)

for _ in range(Q):
    q, x = map(int, input().split())
    if q == 1:
        num[hights[x - 1]] -= 1

        bit.add(hights[x - 1], -1)
        hights[x - 1] += 1
        bit.add(hights[x - 1], +1)

        num[hights[x - 1]] += 1

        if num[base] == 0:
            base += 1
    else:  # q == 2
        if x + base <= Q:
            print(bit.sum(x + base, Q + 1))
        else:
            print(0)
