D = int(input())
X = int(input())
prices = [0] * D
prices[0] = X

for i in range(1, D):
    prices[i] = prices[i-1] + int(input())

Q = int(input())
for _ in range(Q):
    s, t = map(int, input().split())
    if prices[s-1] == prices[t-1]:
        print('Same')
    else:
        print(max((prices[s-1], s), (prices[t-1], t))[1])
