N, M = map(int, input().split())

colors = []
for _ in range(M):
    raw_x, raw_y, c = input().split()
    x, y = int(raw_x), int(raw_y)

    colors.append((x, y, c))

# 下から順番に、かつ黒を優先で処理する。
colors.sort(key=lambda x: (-x[0], 0 if x[2] == "B" else 1))
# print(colors)

prev_x, prev_y = 0, 0
for x, y, c in colors:
    if c == "W":
        if y <= prev_y:
            print("No")
            break
    else:
        prev_x, prev_y = x, max(prev_y, y)
else:
    print("Yes")
