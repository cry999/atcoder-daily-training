from os import getenv
from sys import stdin

input = stdin.buffer.readline


def debug(*args, **kwargs):
    if getenv("DEBUG") == "1":
        print(*args, **kwargs)


class BIT:
    def __init__(self, n: int):
        self.n = n
        self.data = [0] * (self.n + 1)

    def add(self, i: int, x: int):
        while i <= self.n:
            self.data[i] += x
            i += i & -i

    def sum(self, i: int):
        s = 0
        while i > 0:
            s += self.data[i]
            i -= i & -i
        return s

    def range_sum(self, l: int, r: int):
        return self.sum(r) - self.sum(l - 1)

    def lower_bound_prefix_lt(self, x: int):
        """sum(pos) < x を満たす最大 pos を返す"""
        if x <= 0:
            return 0
        pos = 0
        acc = 0
        k = 1 << (self.n.bit_length() - 1)
        while k:
            nxt = pos + k
            if nxt <= self.n and acc + self.data[nxt] < x:
                pos = nxt
                acc += self.data[nxt]
            k >>= 1
        return pos


N, Q = map(int, input().split())

horses = [tuple(map(int, input().split())) for _ in range(N)]

num_inpolites = sum(p == 1 for _, p in horses)
num_polites = sum(p == 2 for _, p in horses)
total_mood = sum(m for m, _ in horses)

MAX_MOOD = 10**6

bit_sum = BIT(MAX_MOOD + 1)
bit_cnt = BIT(MAX_MOOD + 1)
bit_cnt1 = BIT(MAX_MOOD + 1)
bit_cnt2 = BIT(MAX_MOOD + 1)
for mood, politeness in horses:
    bit_sum.add(mood, mood)
    bit_cnt.add(mood, 1)
    bit_cnt1.add(mood, politeness == 1)
    bit_cnt2.add(mood, politeness == 2)

ans = [0] * Q
for q in range(Q):
    w, x, y = map(int, input().split())
    w -= 1

    # 1. 古い値を各種値から削除
    old_mood, old_politeness = horses[w]

    total_mood -= old_mood
    num_inpolites -= old_politeness == 1
    num_polites -= old_politeness == 2

    bit_sum.add(old_mood, -old_mood)
    bit_cnt.add(old_mood, -1)
    bit_cnt1.add(old_mood, -(old_politeness == 1))
    bit_cnt2.add(old_mood, -(old_politeness == 2))

    # 2. 新しい値を各種値に追加
    new_mood, new_politeness = x, y

    horses[w] = (new_mood, new_politeness)

    total_mood += new_mood
    num_inpolites += new_politeness == 1
    num_polites += new_politeness == 2

    bit_sum.add(new_mood, new_mood)
    bit_cnt.add(new_mood, 1)
    bit_cnt1.add(new_mood, (new_politeness == 1))
    bit_cnt2.add(new_mood, (new_politeness == 2))

    if num_polites:
        # 丁寧な馬がいる場合、機嫌 x 2 の合計 - min(z 頭の機嫌の合計) が答え

        # z: 係数が 1 になる馬の数。
        # 全頭丁寧でも、先頭の馬は係数が 1 になるので、max(1, num_inpolites) とする。
        z = max(1, num_inpolites)

        # 係数が 1 になる z 頭の馬を機嫌が悪い順に探したい。
        # NOTE: max_right は politeness == 2 の馬をできるだけ含められるように最大範囲で見ている。
        ri = bit_cnt.lower_bound_prefix_lt(z) + 1
        cnt_inpolite = bit_cnt1.sum(ri)
        cnt_polite = bit_cnt2.sum(ri)
        _sum = bit_sum.sum(ri)

        # politeness == 2 の馬に全ての politeness == 2 の馬を並べることはできない（循環する）ので
        # 少なくとも 1 頭は politeness == 2 の馬が含まれていないといけない。
        if cnt_polite:
            # 係数が 1 になる馬の中に丁寧な馬がいる場合、機嫌 x 2 の合計 - min(z 頭の機嫌の合計) が答え
            # NOTE: max_right を利用しているので、cnt_polite + cnt_inpolite が z より大きい場合がある。
            # この z を超えた分は ri しか取りえないことに注意して補正している。
            ans[q] = total_mood * 2 - (_sum - (cnt_polite + cnt_inpolite - z) * ri)
        else:
            # politeness == 2 の馬を少なくとも 1 頭、係数 1 にする必要があるので、
            # politeness == 2 のなかで最悪の機嫌を持つ馬を持ってくる。
            # worst_mood_in_polites = segtree.max_right(0, f=lambda x: not x.cnt_polite)
            worst_mood_in_polites = bit_cnt2.lower_bound_prefix_lt(1) + 1
            ans[q] = total_mood * 2 - (
                _sum
                # + 1 の部分は、最初に取得した z 頭の中からは最高の機嫌を持つやつを係数 1 の群れから除外する。
                - (cnt_polite + cnt_inpolite - z + 1) * ri
                + worst_mood_in_polites
            )
    else:
        # 全ての馬が丁寧でない場合、機嫌 x 1 の合計が答え
        ans[q] = total_mood

print("\n".join(map(str, ans)))
