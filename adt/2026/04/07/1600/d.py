N, Q = map(int, input().split())

yellow = [0] * (N + 1)
red = [0] * (N + 1)

for _ in range(Q):
    c, x = map(int, input().split())
    if c == 1:
        yellow[x] += 1
    elif c == 2:
        red[x] += 1
    else:  # c == 3
        if yellow[x] == 2 or red[x] == 1:
            print("Yes")
        else:
            print("No")
