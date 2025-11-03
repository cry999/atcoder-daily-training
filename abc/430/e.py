T = int(input())


def z_algorithm(s: str) -> list[int]:
    n = len(s)

    a = [0] * n
    a[0] = n

    i, j, l = 1, 0, n
    while i < l:
        # i から始まる文字列と先頭から始まる文字列の共通接頭辞の長さを求める
        while i+j < l and s[j] == s[i+j]:
            j += 1
        if not j:  # 共通接頭辞がない場合
            i += 1
            continue
        a[i] = j  # s[0:j] == s[i:i+j]

        k = 1
        while k < min(l-i, j-a[k]):
            a[i+k] = a[k]
            k += 1
        i, j = i+k, j-k
    return a


for _ in range(T):
    A = input()
    B = input()

    # n = len(A)
    # step = 1
    # while step << 1 <= n:
    #     step <<= 1
    #
    # while step > 0:
    #     try:
    #         i = A.index(B[:min(step, len(B))])
    #         while True:
    #             a1, a2 = A[:i], A[i:]
    #             b1, b2 = B[n-i:], B[:n-i]
    #             if a1 == b1 and a2 == b2:
    #                 print(len(a1))
    #                 break
    #             i = A.index(B[:min(step, len(B))], i+1)
    #     except ValueError:
    #         step >>= 1
    #         continue
    #     break
    # else:
    #     print(-1)
    z = z_algorithm(B+A+A)
    for i, lcp in enumerate(z[len(B):len(B)+len(A)]):
        if lcp >= len(B):
            print(i)
            break
    else:
        print(-1)
