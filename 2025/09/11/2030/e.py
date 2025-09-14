X, A, D, N = map(int, input().split())


# X に最も近い A + (m-1)*D を満たす m を二分探索で探す
def search(X: int) -> int:
    if D == 0:
        return abs(A - X)

    left, right = 1, N

    while left <= right:
        mid = (left + right) // 2
        a = A + (mid - 1) * D
        if a == X:
            return 0
        elif (D > 0 and a < X) or (D < 0 and a > X):
            left = mid + 1
        else:
            right = mid - 1

    # print(left, right)
    left = min(left, N)
    right = max(right, 1)
    # print(
    #     abs(A + (left - 1) * D - X),
    #     abs(A + (right - 1) * D - X),
    # )
    return min(
        abs(A + (left - 1) * D - X),
        abs(A + (right - 1) * D - X),
    )


print(search(X))
