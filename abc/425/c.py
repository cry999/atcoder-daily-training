N, Q = map(int, input().split())
A = list(map(int, input().split()))
cum = [0] * (N+1)

for i in range(N):
    cum[i+1] = cum[i] + A[i]

offset = 0
for _ in range(Q):
    query = tuple(map(int, input().split()))
    if query[0] == 1:
        _, c = query
        offset = (offset + c) % N
    elif query[0] == 2:
        _, le, ri = query
        # print('---')
        # print(le, ri)
        le = (le+offset) % N
        if le == 0:
            le = N
        ri = (ri+offset) % N
        if ri == 0:
            ri = N
        # print(le, ri)
        # print('---')
        if le <= ri:
            print(cum[ri] - cum[le-1])
        else:
            print(cum[N] - cum[le-1] + cum[ri])
