class SegTree:
    def __init__(self, n: int):
        self.n = 1
        while self.n < n:
            self.n *= 2

        self.data = [0] * (2 * self.n)

    def add(self, i: int, x: int):
        i += self.n
        self.data[i] += x
        while i >= 2:
            i //= 2
            self.data[i] = self.data[i * 2] + self.data[i * 2 + 1]

    def query(self, l: int, r: int) -> int:
        return self._query(l, r, 1, 0, self.n)

    def _query(self, l: int, r: int, k: int, a: int, b: int) -> int:
        if r <= a or b <= l:
            return 0
        if l <= a and b <= r:
            return self.data[k]

        q1 = self._query(l, r, 2 * k, a, (a + b) // 2)
        q2 = self._query(l, r, 2 * k + 1, (a + b) // 2, b)

        return q1 + q2


N = int(input())
S = list(input())
Q = int(input())

segtrees = [SegTree(N) for _ in range(26)]

for i, c in enumerate(S):
    x = ord(c) - ord("a")
    segtrees[x].add(i, 1)

for _ in range(Q):
    q, *args = input().split()

    if q == "1":
        raw_x, new_c = args
        x = int(raw_x) - 1
        old_c, S[x] = S[x], new_c

        segtrees[ord(old_c) - ord("a")].add(x, -1)
        segtrees[ord(new_c) - ord("a")].add(x, +1)

    else:  # q == "2"
        l, r = map(lambda x: int(x) - 1, args)
        # print(f"=== {l=}, {r=} ===")
        cnt = [0] * 26
        min_c, max_c = 26, -1
        for c in range(26):
            cnt[c] = segtrees[c].query(l, r + 1)
            if cnt[c] > 0:
                min_c = min(min_c, c)
                max_c = max(max_c, c)
        # print(f"min_c: {chr(min_c + ord('a'))}, max_c: {chr(max_c + ord('a'))}")
        offset = 0
        for c in range(min_c, max_c + 1):
            # min_c より大きく max_c より小さい文字が全てこの範囲に含まれていること.
            # min_c と max_c は途中からの可能性があるので全て含んでいる必要はない。
            if min_c < c < max_c and cnt[c] != segtrees[c].query(0, N + 1):
                # print("No: all include")
                print("No")
                break

            # sort されているかの調査
            la = l + offset
            ra = la + cnt[c]
            # print(f"{la=}, {ra=}")
            if not (ra <= r + 1 and cnt[c] == segtrees[c].query(la, ra)):
                # print("No: not sorted")
                print("No")
                break
            offset += cnt[c]
        else:
            print("Yes")
