N, Q = map(int, input().split())
(*P,) = map(int, input().split())
R = [0] * N
for i in range(N):
    P[i] -= 1
    R[P[i]] = i


target = 0
for _ in range(Q):
    q, *args = map(int, input().split())

    if q == 1:
        x, y = args
        x, y = x - 1, y - 1
        if target == 0:
            p1, p2 = P[x], P[y]
            P[x], P[y] = P[y], P[x]
            R[p1], R[p2] = R[p2], R[p1]
        else:
            r1, r2 = R[x], R[y]
            R[x], R[y] = R[y], R[x]
            P[r1], P[r2] = P[r2], P[r1]
    else:
        target = 1 - target

if target == 0:
    print(*[p + 1 for p in P])
else:
    print(*[r + 1 for r in R])
