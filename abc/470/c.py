N, Q = map(int, input().split())

A = [0] * N


s = 0
not_zero = set()
for _ in range(Q):
    q, *args = map(int, input().split())

    if q == 1:
        x = args[0] - 1
        s ^= A[x]
        A[x] += 1
        s ^= A[x]

        not_zero.add(x)
    else:
        new_not_zero = set()
        for x in not_zero:
            s ^= A[x]
            A[x] -= 1
            s ^= A[x]

            if A[x] > 0:
                new_not_zero.add(x)

        not_zero = new_not_zero

    print(s)
