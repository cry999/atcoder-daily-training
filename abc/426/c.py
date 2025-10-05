# NQ = 2 x 10^11 なのでブルートフォースは無理
N, Q = map(int, input().split())
minimum = 1
m = {i+1: 1 for i in range(N)}

op = 0
for _ in range(Q):
    X, Y = map(int, input().split())
    if X < minimum:
        op += 1
        print(0)
        continue
    count = 0
    for i in range(minimum, X+1):
        c = m.get(i, 0)
        m[i] = 0
        m[Y] += c
        count += c
        op += 1
        pass
    # print(count, m)
    print(count)
    minimum = X+1

# print(op)
