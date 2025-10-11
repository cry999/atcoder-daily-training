N, Q = map(int, input().split())


class SegmentTree:
    def __init__(self, data: list[int]):
        self.size = 1
        n = len(data)
        while self.size < n:
            self.size <<= 1
        self.data = [0] * (2 * self.size)

        for i, d in enumerate(data):
            self.data[i+self.size] = d

    def __debug(self, *values: object):
        # print(*values)
        pass

    def __debug_tree(self):
        # self.__debug('--- Segment Tree ---')
        # i = 0
        # while (1 << i) <= 2*self.size:
        #     self.__debug(*self.data[1 << i: (1 << (i+1))])
        #     i += 1
        # self.__debug('--------------------')
        pass

    def query(self, left: int, right: int) -> int:
        self.__debug('query', left, right)
        self.__debug_tree()

        def _query(
            # クエリ対象区間 [target_left, target_right)
            target_l: int, target_r: int,
            # 探索区間 [search_left, search_right)
            search_l: int, search_r: int,
            # segment_tree のノード番号
            idx: int,
        ) -> int:
            self.__debug('__query', target_l, target_r,
                         search_l, search_r, idx)
            if target_r <= search_l or search_r <= target_l:
                # 探索対象区間がクエリ区間に全く含まれない場合
                return -1
            if target_l <= search_l and search_r <= target_r:
                # 探索対象区間がクエリ区間に完全に含まれる場合
                return self.data[idx]
            # クエリ対象区間と探索区間が一部重なる場合は二分探索
            search_m = (search_l + search_r) // 2
            return max(
                # left 側の子ノードを探索
                _query(target_l, target_r, search_l, search_m, idx*2),
                _query(target_l, target_r, search_m, search_r, idx*2+1),
            )
        return _query(left, right, 0, self.size, 1)

    def update(self, pos: int, x: int):
        self.__debug('update', pos, x)
        pos += self.size
        self.data[pos] = x

        while pos >= 2:
            self.__debug(pos)
            pos >>= 1
            self.data[pos] = max(self.data[pos*2], self.data[pos*2+1])
        self.__debug_tree()


st = SegmentTree([0]*N)

for _ in range(Q):
    q, x, y = map(int, input().split())
    if q == 1:
        pos, x = x, y

        st.update(pos-1, x)
    else:  # q == 2
        l, r = x, y
        print(st.query(l-1, r-1))
