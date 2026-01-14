N, Q = map(int, input().split())
S = input()

offset = 0
for _ in range(Q):
    t, x = map(int, input().split())
    if t == 1:
        offset += x
        offset %= N
    else:
        print(S[(x - 1 - offset) % N])
