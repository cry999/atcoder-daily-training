INF = 10**18

T = int(input())
for _ in range(T):
    N = int(input())
    (*A,) = map(int, input().split())

    # AVG = (a1 + a2) // 2 + (a2 + a3) // 2 + ... + (aN-1 + aN) // 2
    #     = (a1 + a2 - odd?(a1+a2)) / 2 + (a2 + a3 - odd?(a2+a3)) / 2 + ... + (aN-1 + aN - odd?(aN-1+aN)) / 2
    #     = (a1 + ... + aN) - (a1 + aN + odd?(a1+a2) + ... + odd?(a{N-1}+aN)) / 2
    # なので、a1, aN の組み合わせと、その時作れる odd? の最大値を求めれば良い 。
    # O(T N^2) かかるが、 N <= 30 なので間に合う。

    O = sum(a % 2 == 1 for a in A)
    E = sum(a % 2 == 0 for a in A)
    S = sum(A)

    max_num = [[0, 0], [0, 0]]
    for a in A:
        if a > max_num[a % 2][0]:
            max_num[a % 2][:] = [a, max_num[a % 2][0]]
        elif a > max_num[a % 2][1]:
            max_num[a % 2][1] = a

    ans = S
    # 両端奇数
    n1, n2 = max_num[1]
    ans = min(ans, S - (n1 + n2 + 2 * min(O - 1, E)) // 2)
    # 両端偶数
    n1, n2 = max_num[0]
    ans = min(ans, S - (n1 + n2 + 2 * min(O, E - 1)) // 2)
    # 偶奇の組み合わせ
    n1, n2 = max_num[0][0], max_num[1][0]
    ans = min(ans, S - (n1 + n2 + 2 * min(O, E) - 1) // 2)
    print(ans)
