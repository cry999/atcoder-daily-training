# index 操作を管理する
# 最初は頭から計算する。query = 2 を受け取ったらお尻から計算する

N, Q = map(int, input().split())
A = [i+1 for i in range(N)]
from_head = True

for _ in range(Q):
    c, *query = map(int, input().split())
    # print(c, query)
    if c == 1:  # change number
        x, y = query
        if from_head:
            A[x-1] = y
        else:
            A[N-x] = y
    elif c == 2:  # reverse
        from_head = not from_head
    else:  # query[0] == '3' # print
        x, *_ = query
        if from_head:
            print(A[x-1])
        else:
            print(A[N-x])
