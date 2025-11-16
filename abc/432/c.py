# N: 子供の人数, X: 小さな飴の重さ, Y: 大きな飴の重さ
N, X, Y = map(int, input().split())
# A[i]: i 番目の子供に配る飴の総数
*A, = map(int, input().split())


max_weight = Y*A[0]
min_weight = Y*A[0] - (Y-X)*min(A[0], Y*A[0]//(Y-X))
for a in A:
    if Y*a % (Y-X) != max_weight % (Y-X):
        print(-1)
        break
    max_weight = min(max_weight, Y*a)
    min_weight = max(min_weight, Y*a-(Y-X)*min(a, Y*a//(Y-X)))
else:
    if min_weight > max_weight:
        print(-1)
    else:
        print(sum((max_weight-X*a) // (Y-X) for a in A))
