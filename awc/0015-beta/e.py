from typing import Self


class SegmentTree:
    def __init__(self, n: int) -> Self:
        self.n = 1
        while self.n < n:
            self.n <<= 1
        self.data = [0] * (self.n << 1)

    def add(self, i: int, v: int) -> None:
        i += self.n
        self.data[i] += v

        while i > 1:
            i >>= 1
            self.data[i] += v

    def set(self, i: int, v: int) -> None:
        i += self.n
        self.data[i] = v

        while i > 1:
            i >>= 1
            self.data[i] = self.data[2 * i] + self.data[2 * i + 1]

    def query(self, l: int, r: int) -> int:
        l += self.n
        r += self.n

        lv, rv = 0, 0
        while l < r:
            if l & 1:
                lv += self.data[l]
                l += 1
            if r & 1:
                r -= 1
                rv += self.data[r]

            l >>= 1
            r >>= 1

        return lv + rv


N, Q = map(int, input().split())
(*P,) = map(int, input().split())

segtree = SegmentTree(N)

queries = []
for q in range(Q):
    l, r = map(int, input().split())
    queries.append((r - 1, l - 1, q))

queries.sort()

cur = 0
# i が出現する最後の位置
last_index: dict[int, int] = {P[cur]: cur}

segtree.set(cur, 1)

ans = [0] * Q

for r, l, q in queries:
    while cur < r:
        cur += 1
        p = P[cur]
        if p in last_index:
            segtree.set(last_index[p], 0)
        last_index[p] = cur
        segtree.set(cur, 1)

    ans[q] = segtree.query(l, r + 1)

for a in ans:
    print(a)
