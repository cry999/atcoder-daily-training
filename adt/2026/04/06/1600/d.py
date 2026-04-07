N = int(input())
(*P,) = map(int, input().split())
R = [0] * (N + 1)
for i in range(N):
    R[P[i]] = i

Q = int(input())
for _ in range(Q):
    a, b = map(int, input().split())
    if R[a] < R[b]:
        print(a)
    else:
        print(b)
