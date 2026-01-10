from typing import Callable

T = int(input())


def merge_sort(a: list[int], cmp: Callable[[int, int], bool]):
    if len(a) <= 1:
        return
    m = len(a) // 2
    x = a[:m]
    y = a[m:]
    merge_sort(x, cmp)
    merge_sort(y, cmp)

    i, j = 0, 0
    while i < m or j < len(a) - m:
        if i == m:
            a[i + j] = y[j]
            j += 1
        elif j == len(a) - m:
            a[i + j] = x[i]
            i += 1
        elif cmp(x[i], y[j]):
            a[i + j] = x[i]
            i += 1
        else:
            a[i + j] = y[j]
            j += 1
    return


for _ in range(T):
    A = input()
    B = input()

    N = len(A)
    N3 = 3 * N
    C = B + A * 2

    z = [0] * N3
    i, j = 1, 0
    while i < N3:
        # i を固定して、一致している限り j を伸ばす。
        while i + j < N3 and C[j] == C[i + j]:
            j += 1
        # i から始まる長さ j の文字列と先頭から j 文字が一致する。
        z[i] = j

        if j == 0:
            # 一致する部分がないなら、次の文字から再スタート
            i += 1
            continue

        k = 1
        while k < j and k + z[k] < j:
            z[i + k] = z[k]
            k += 1

        i += k
        j -= k

    for i in range(N):
        if z[i + N] >= N:
            print(i)
            break
    else:
        print(-1)
