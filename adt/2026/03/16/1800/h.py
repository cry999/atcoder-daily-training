from atcoder.string import z_algorithm

T = int(input())

for _ in range(T):
    A = input()
    B = input()

    n = len(A)
    assert n == len(B)

    z = [0] * (3 * n)
    z[0] = 3 * n
    i, j = 1, 0

    z = z_algorithm(B + A + A)

    ans = -1
    for i in range(n, 2 * n):
        if z[i] >= n:
            ans = i - n
            break
    print(ans)
