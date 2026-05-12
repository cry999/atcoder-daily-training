from math import lcm

N, X, Y = map(int, input().split())
P, T = [-1] * (N - 1), [-1] * (N - 1)

for i in range(N - 1):
    P[i], T[i] = map(int, input().split())

l = lcm(*P)
time = [i for i in range(l)] * l
for i in range(l):
    time[i] += X

    for p, t in zip(P, T):
        if time[i] % p != 0:
            time[i] += p - time[i] % p
        time[i] += t

    time[i] += Y


Q = int(input())
for _ in range(Q):
    q = int(input())
    print(q + time[q % l] - q % l)
