from sortedcontainers import SortedList

A = SortedList()

Q = int(input())
for _ in range(Q):
    q, *args = map(int, input().split())

    # print(f"[DEBUG] {q=}, {args=}, {A=}")
    if q == 1:
        x = args[0]
        A.add(x)
    elif q == 2:
        x, k = args
        i = A.bisect_right(x)
        if i - k >= 0:
            print(A[i - k])
        else:
            print(-1)
    else:  # q == 3
        x, k = args
        i = A.bisect_left(x)
        if i + k - 1 < len(A):
            print(A[i + k - 1])
        else:
            print(-1)
