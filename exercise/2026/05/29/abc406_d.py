H, W, N = map(int, input().split())

x_axis = [[] for _ in range(H + 1)]
y_axis = [[] for _ in range(W + 1)]

for _ in range(N):
    x, y = map(int, input().split())
    x_axis[x].append(y)
    y_axis[y].append(x)

Q = int(input())
for _ in range(Q):
    q, *args = map(int, input().split())

    if q == 1:
        x = args[0]
        ans = 0
        while x_axis[x]:
            y = x_axis[x].pop()
            if y_axis[y]:
                ans += 1
        print(ans)
    else:
        y = args[0]
        ans = 0
        while y_axis[y]:
            x = y_axis[y].pop()
            if x_axis[x]:
                ans += 1
        print(ans)
