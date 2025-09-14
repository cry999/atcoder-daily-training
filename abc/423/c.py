N, R = map(int, input().split())
L = list(map(int, input().split()))

count = 0
if R > 0:  # 左の部屋の戸締りを確認する必要あり
    # 左の部屋の戸締りの回数を count に加算
    try:
        mlz = L.index(0)  # Most Left Zero
    except ValueError:
        mlz = N
    # print('mlz', mlz)
    # print('search', L[mlz:R])
    if mlz > R - 1:
        # mlz が R-1 以上なら、左の部屋の戸締りは全て確認済み
        pass
    else:
        count += sum(2 if lock == 1 else 1 for lock in L[mlz:R])
if R < N:  # 右の部屋の戸締りを確認する必要あり
    # 右の部屋の戸締りの回数を count に加算
    try:
        mrz = N - 1 - L[::-1].index(0)  # Most Right Zero
    except ValueError:
        mrz = -1
    # print('mrz', mrz)
    # print('search', L[R:mrz+1])
    if mrz <= R - 1:
        # mrz が R-1 以下なら、右の部屋の戸締りは全て確認済み
        pass
    else:
        count += sum(2 if lock == 1 else 1 for lock in L[R:mrz+1])


print(count)
