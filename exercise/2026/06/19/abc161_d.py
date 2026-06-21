K = int(input())

X = []
X.append(set(range(1, 10)))

cnt = len(X[0])
while cnt < K:
    Y = set()
    d = len(X) - 1
    pow10 = pow(10, d)
    for x in X[-1]:
        a = x % 10
        Y.add(x * 10 + a)
        if a - 1 >= 0:
            Y.add(x * 10 + a - 1)
        if a + 1 <= 9:
            Y.add(x * 10 + a + 1)

    X.append(Y)
    cnt += len(Y)

lunlun = []
for x in X:
    lunlun.extend(x)

lunlun.sort()

print(lunlun[K - 1])
