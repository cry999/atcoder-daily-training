T = int(input())

for _ in range(T):
    N = int(input())
    (*R,) = map(int, input().split())

    op = 0
    # 左から右にみる
    for i in range(N - 1):
        if abs(R[i] - R[i + 1]) <= 1:
            continue
        if R[i] > R[i + 1]:
            op += R[i] - R[i + 1] - 1
            R[i] = R[i + 1] + 1
        else:
            op += R[i + 1] - R[i] - 1
            R[i + 1] = R[i] + 1

    # 右から左にみる
    for i in range(N - 2, -1, -1):
        if abs(R[i] - R[i + 1]) <= 1:
            continue
        if R[i] > R[i + 1]:
            op += R[i] - R[i + 1] - 1
            R[i] = R[i + 1] + 1
        else:
            op += R[i + 1] - R[i] - 1
            R[i + 1] = R[i] + 1

    print(op)
