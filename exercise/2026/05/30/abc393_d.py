N = int(input())
S = input()

# 1 の S の中でのインデックスと 1 だけの中でのインデックスを利用する
ones = []

for i, s in enumerate(S):
    if s == "1":
        ones.append(i)

eff = [(i - j) for i, j in enumerate(ones)]
eff.sort(reverse=True)

# print(eff)
total = sum(eff)

# |(l + i) - ones[i]| の総和を l を動かしながら求めたい。
# 毎回計算すると O(N^2) になってしまうので、border の位置を記憶して、
# 絶対値計算を回避することで全体で O(N) で計算するようにする。
# border: l + i - ones[i] >= 0 を満たす最小の i
border = 0
ans = N * N
for l in range(N):
    while border < len(ones) and l + eff[border] >= 0:
        total -= 2 * eff[border]
        border += 1
    ans = min(ans, (2 * border - len(ones)) * l - total)

print(ans)
