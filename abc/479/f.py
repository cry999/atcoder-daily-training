from atcoder.fenwicktree import FenwickTree

N = int(input())
(*S,) = map(int, input().split())
(*T,) = map(int, input().split())


si = sorted(range(N), key=lambda i: S[i])
ti = sorted(range(N), key=lambda i: T[i])

# rank_t[i] := T[i] のソート順位 (人 i の並び終わり後の左からの番号)
rank_t = [0] * N
for t, i in enumerate(ti):
    rank_t[i] = t

ans = 0
for s, i in enumerate(si):
    # S[i] := 人 i の最初の位置
    # s := 人 i のソート順位 (人 i の並び前の左からの番号)
    # S[i] - s := 人 i の左にある空きますの数
    # T[i] = t := 同様に、最終的な位置での人 i の左にあるあきますの数
    # この差を埋める必要があるので、あきますに対する移動回数は |(T[i] - t) - (S[i] - s)|
    t = rank_t[i]
    ans += abs((T[i] - t) - (S[i] - s))

# 人同士の交換を数える。
# si -> ti の変化は、人同士の交換が必須。(あきますに移動しても、順位は変わらない)
# つまり, si -> ti の変化は転倒数に等しい。

bit = FenwickTree(N)
for s, i in enumerate(si):
    t = rank_t[i]

    ans += bit.sum(t + 1, N)
    bit.add(t, 1)

print(ans)
