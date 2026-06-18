from bisect import bisect_right

N, Q = map(int, input().split())
(*A,) = map(int, input().split())

for _ in range(Q):
    K = int(input())

    offset = 0
    while True:
        i = bisect_right(A, K + offset)
        # 前回までの操作で増やした A の個数分を除く
        new_offset = i - offset
        if not new_offset:
            print(K + offset)
            break
        offset += new_offset
