from atcoder.fenwicktree import FenwickTree

MOD = 998244353


N = int(input())
(*P,) = map(int, input().split())

bit = FenwickTree(N + 1)
for i in range(N + 1):
    bit.data[i] = (i + 1) & -(i + 1)

pow2 = [1] * (N + 1)
for i in range(N):
    pow2[i + 1] = pow2[i] * 2 % MOD

l, r = 0, N - 1
is_reversed = False
ans = 0

for i in range(N, 1, -1):
    pl = P[l] if not is_reversed else P[r]
    pr = P[r] if not is_reversed else P[l]

    # 1. 反転判定
    if pl > pr:
        ans += 1
        is_reversed = not is_reversed

    x = max(pl, pr)  # 末尾の値
    g: int = i - bit.sum(0, x)  # 末尾の値より大きい値の個数  # pyright: ignore[reportAny]

    if g > 0:
        ans += pow2[g - 1]

    ans %= MOD
    bit.add(x, -1)

    if P[l] == x:
        l += 1
    else:
        r -= 1
print(ans)
