from sortedcontainers import SortedList


T = int(input())

for _ in range(T):
    N, M = map(int, input().split())
    (*A,) = map(int, input().split())

    sorted_list = SortedList(A)

    for _ in range(M):
        # 最大値を分割する
        a = sorted_list[-1]
        i1 = sorted_list.bisect_left(a // 2)
        i2 = sorted_list.bisect_left(a // 2 + (a % 2))
        mi = len(sorted_list) // 2
        if i2 < mi:
            median_max = max(a // 2 + (a % 2), sorted_list[mi - 1] if mi > 0 else 0)
        elif i1 < mi:
            median_max = sorted_list[mi]
        else:
            median_max = min(a // 2, sorted_list[mi + 1] if mi + 1 < N else 0)

        # 最小値を分割する
        mi = len(sorted_list) // 2
        median_min = sorted_list[mi]

        if median_min <= median_max:
            a = sorted_list.pop()
            sorted_list.add(a // 2)
            sorted_list.add(a // 2 + (a % 2))
        else:
            a = sorted_list.pop(0)
            sorted_list.add(a // 2)
            sorted_list.add(a // 2 + (a % 2))

    print(sorted_list[len(sorted_list) // 2])
