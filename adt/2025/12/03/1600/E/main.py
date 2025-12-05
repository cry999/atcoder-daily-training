N, Q = map(int, input().split())
A = [i+1 for i in range(N)]

offset = 0
for _ in range(Q):
    query, *param = map(int, input().split())
    if query == 1:
        p, x = param
        A[(offset+p-1) % N] = x
    elif query == 2:
        p = param[0]
        print(A[(offset+p-1) % N])
    else:
        k = param[0]
        offset = (offset+k) % N
