import bisect as b


class SegmentTree:
    def __init__(self, data: list[int], initial=0):
        self.size = 1
        n = len(data)
        while self.size < n:
            self.size <<= 1

        self.data = [initial] * (2 * self.size)
        for i, d in enumerate(data):
            self.data[i+self.size] = d

    def update(self, i: int, v: int):
        '''0-indexed'''
        pos = i + self.size
        self.data[pos] = v

        while pos > 1:
            pos >>= 1
            self.data[pos] = min(self.data[2*pos], self.data[2*pos+1])

    def query(self, left: int, right: int) -> int:
        '''0-indexed, [left, right)'''
        return self._query(left, right, 0, self.size, 1)

    def _query(
        self,
        target_l: int, target_r: int,
        search_l: int, search_r: int,
        idx: int,
    ) -> int:
        if target_r <= search_l or search_r <= target_l:
            return float('inf')
        if target_l <= search_l and search_r <= target_r:
            return self.data[idx]
        search_m = (search_l + search_r) // 2
        return min(
            self._query(target_l, target_r, search_l, search_m, 2*idx),
            self._query(target_l, target_r, search_m, search_r, 2*idx+1),
        )

    def _debug_tree(self):
        i = 0
        while (1 << i) < 2 * self.size:
            print(self.data[1 << i:1 << (i+1)])
            i += 1


N, L, R = map(int, input().split())
X = list(map(int, input().split()))

st = SegmentTree([float('inf')]*N, initial=float('inf'))
st.update(0, 0)  # 最初の足場は 0 回で到達

for i in range(1, N):
    j_min, j_max = b.bisect_left(X, X[i]-R), b.bisect_right(X, X[i]-L)
    v = st.query(j_min, j_max)
    st.update(i, v+1)
print(st.query(N-1, N))
