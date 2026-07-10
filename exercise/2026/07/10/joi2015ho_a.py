N, M = map(int, input().split())
(*P,) = map(int, input().split())
# prices[i] := i と i+1 の間の鉄道の (切符運賃, IC 運賃, IC カード費用)
prices = [tuple(map(int, input().split())) for _ in range(N - 1)]

# 各鉄道を何回利用するかを計算する。
# num[i] := i と i+1 の間の鉄道を利用した回数
num = [0] * (N + 1)
cur = P[0]
for p in P[1:]:
    num[min(cur, p)] += 1
    num[max(cur, p)] -= 1
    cur = p

total_price = 0
for i in range(N - 1):
    num[i + 1] += num[i]
    a, b, c = prices[i]
    total_price += min(a * num[i + 1], b * num[i + 1] + c)

print(total_price)
