from typing import Callable, Iterable

Func = Callable[[Iterable[int]], int]


class SegmentTree:
    def __init__(self, n: int, func: Func = max, init: int = 0):
        self._size = 1
        while self._size < n:
            self._size <<= 1
        self._func = func
        self._init = init
        self._data = [init] * (2 * self._size)

    def update(self, i: int, v: int):
        i += self._size
        self._data[i] = v

        while i > 1:
            i >>= 1
            self._data[i] = self._func(self._data[i * 2], self._data[i * 2 + 1])

    def query(self, left: int, right: int) -> int:
        return self._query((left, right), (0, self._size), 1)

    def _query(self, target: tuple[int], search: tuple[int], idx: int) -> int:
        tl, tr, sl, sr = *target, *search
        if tr <= sl or sr <= tl:
            return self._init
        if tl <= sl and sr <= tr:
            return self._data[idx]
        sm = (sl + sr) // 2
        return self._func(
            self._query((tl, tr), (sl, sm), 2 * idx),
            self._query((tl, tr), (sm, sr), 2 * idx + 1),
        )


N = int(input())
(*h,) = map(int, input().split())
(*a,) = map(int, input().split())

st = SegmentTree(N + 1)

for hi, ai in zip(h, a):
    # hi 未満の単調増加列の最大価値を取得
    v = st.query(0, hi)
    # それに ai を加えたものが hi で終わる最大価値
    st.update(hi, ai + v)

print(st.query(0, N + 1))
