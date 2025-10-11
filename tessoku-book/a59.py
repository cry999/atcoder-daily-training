from typing import Callable, Iterable


def _sum(*args: int) -> int:
    return sum(args)


class SegmentTree:
    def __init__(
        self,
        n: int,
        func: Callable[[Iterable[int]], int] = _sum,
        init: int = 0,
    ):
        self._func = func
        self._size = 1
        self._init_value = init
        while self._size < n:
            self._size <<= 1
        self._data = [self._init_value] * (self._size*2)

    def update(self, i: int, v: int):
        i += self._size
        self._data[i] = v

        while i > 1:
            i >>= 1
            self._data[i] = self._func(self._data[2*i], self._data[2*i+1])

    def query(self, left: int, right: int) -> int:
        return self._query(left, right, 0, self._size, 1)

    def _query(
        self,
        target_l: int, target_r: int,
        search_l: int, search_r: int,
        idx: int,
    ) -> int:
        if target_r <= search_l or search_r <= target_l:
            return self._init_value
        if target_l <= search_l and search_r <= target_r:
            return self._data[idx]
        search_m = (search_l + search_r) // 2
        return self._func(
            self._query(target_l, target_r, search_l,  search_m, 2*idx),
            self._query(target_l, target_r, search_m,  search_r, 2*idx+1),
        )


N, Q = map(int, input().split())
st = SegmentTree(N)

for _ in range(Q):
    q, x, y = map(int, input().split())
    if q == 1:
        pos, x = x, y
        st.update(pos-1, x)
    else:  # q == 2
        l, r = x-1, y-1
        print(st.query(l, r))
