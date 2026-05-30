T = int(input())

for _ in range(T):
    X1, Y1, R1, X2, Y2, R2 = map(int, input().split())

    d = (X1 - X2) ** 2 + (Y1 - Y2) ** 2
    r_max = R1 + R2
    r_min = abs(R1 - R2)

    if r_min**2 <= d <= r_max**2:
        print("Yes")
    else:
        print("No")
