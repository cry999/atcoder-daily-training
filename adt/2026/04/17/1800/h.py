MOD = 998244353
INV_2 = pow(2, MOD - 2, MOD)


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
            self.data[p - 1] %= MOD
            p += p & -p

    def sum(self, left: int, right: int) -> int:
        assert 0 <= left <= right <= self._n

        return self._sum(right) - self._sum(left)

    def _sum(self, r: int) -> int:
        s = 0
        while r > 0:
            s += self.data[r - 1]
            s %= MOD
            r -= r & -r

        return s


N = int(input())
(*A,) = map(int, input().split())

# A の値を [0, N] に圧縮することで BIT で処理できるようにする。
# 圧縮方法はソートした際のインデックス。
# 重複排除まではしなくても大丈夫そうなのでしない。
index = {}
for i, a in enumerate(sorted(A)):
    if a not in index:
        index[a] = i

bit = FenwickTree(N + 1)
bit.add(index[A[0]], INV_2)

d = INV_2
m = 2
ans = 0
for i in range(1, N):
    d *= INV_2
    d %= MOD

    a = A[i]
    s = bit.sum(0, index[a] + 1)
    ans += m * s
    ans %= MOD

    bit.add(index[a], d)

    m *= 2
    m %= MOD

print(ans)
