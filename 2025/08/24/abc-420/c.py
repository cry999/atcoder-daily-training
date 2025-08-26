N, Q = map(int, input().split())

A = list(map(int, input().split()))
B = list(map(int, input().split()))

C = sum(map(min, zip(A, B)))

for _ in range(Q):
    c, x, v = input().split()
    x, v = int(x)-1, int(v)

    old = min(A[x], B[x])

    if c == 'A':
        A[x] = v
    else:
        B[x] = v

    C += -old + min(A[x], B[x])
    print(C)
