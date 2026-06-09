from atcoder.fenwicktree import FenwickTree

S = input()
ATCODER = "atcoder"
index = {c: i for i, c in enumerate(ATCODER)}
N = len(ATCODER)

bit = FenwickTree(N)
ans = 0
for c in S:
    j = index[c]
    ans += bit.sum(j, N)
    bit.add(j, 1)
print(ans)
