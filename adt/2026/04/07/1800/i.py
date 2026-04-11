T = int(input())

for _ in range(T):
    N = int(input())
    (*A,) = map(int, input().split())

    LIS = 0

    # left[i]: A[i] を末尾とするような LIS の長さ
    left = [0] * N
    # L[x]: 長さ x の LIS の最後の要素として考えられる最小値
    L = [float("inf")] * (N + 1)
    L[0] = 0

    for i in range(N):
        a = A[i]

        lo, hi = 0, N + 1
        while hi - lo > 1:
            mi = (lo + hi) // 2
            if a <= L[mi]:
                hi = mi
            else:
                lo = mi

        L[lo + 1] = a
        left[i] = lo + 1
        LIS = max(LIS, lo + 1)

    # print(f"{LIS=}")
    # print("left:", *left)
    # print("L:", *L)

    right = [0] * N
    # R[x]: 長さ x の LIS の最初の要素として考えられる最大値
    R = [0] * (N + 1)
    R[0] = float("inf")

    for i in range(N - 1, -1, -1):
        a = A[i]

        lo, hi = 0, N + 1
        while hi - lo > 1:
            mi = (lo + hi) // 2
            if a >= R[mi]:
                hi = mi
            else:
                lo = mi

        R[lo + 1] = a
        right[i] = lo + 1

    # print("right:", *right)
    # print("R:", *R)

    ans = [i + 1 for i in range(N) if left[i] + right[i] - 1 == LIS]
    print(len(ans))
    print(*ans)
