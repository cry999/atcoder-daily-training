# すでに登場している数をカウントする。
# 逆転している (i, j) の組み合わせは j を for 分で回して
# [j+1, N] のなかですでに登場しているものを合算するだけ。

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
            self._data[i] = self._func(self._data[i*2], self._data[i*2+1])

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
            self._query((tl, tr), (sl, sm), 2*idx),
            self._query((tl, tr), (sm, sr), 2*idx+1),
        )


N = int(input())
A = list(map(int, input().split()))


def _sum(*args: int) -> int:
    return sum(args)


st = SegmentTree(N+1, func=_sum, init=0)
ans = 0
for a in A:
    v = st.query(a+1, N+1)
    ans += v
    st.update(a, 1)
print(ans)
