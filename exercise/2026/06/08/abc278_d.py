N = int(input())
(*A,) = map(int, input().split())

Q = int(input())
last_query = [-1] * N
reset = 0
last_reset = -2
for j in range(Q):
    q, *args = map(int, input().split())
    if q == 1:
        x = args[0]
        reset = x
        last_reset = j
    elif q == 2:
        i, x = args
        i -= 1
        if last_query[i] < last_reset:
            A[i] = reset
        last_query[i] = j
        A[i] += x
    else:  # q == 3
        i = args[0] - 1
        if last_query[i] < last_reset:
            A[i] = reset
        last_query[i] = j
        print(A[i])
