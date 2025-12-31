N, M = map(int, input().split())

nodes = []

for _ in range(M):
    _x, _y, c = input().split()
    x, y = int(_x), int(_y)
    nodes.append((x, y, 0 if c == "W" else 1))

nodes.sort()

max_black = N
for x, y, c in nodes:
    if c == 0:  # white
        max_black = y - 1
    else:  # black
        if y > max_black:
            print("No")
            break
else:
    print("Yes")
