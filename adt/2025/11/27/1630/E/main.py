x1, y1, x2, y2 = map(int, input().split())

dxy = [(1, 2), (2, 1)]

points_from_1 = set()
points_from_2 = set()

for dx, dy in dxy:
    for sign_x in [-1, 1]:
        for sign_y in [-1, 1]:
            points_from_1.add((x1+sign_x*dx, y1+sign_y*dy))
            points_from_2.add((x2+sign_x*dx, y2+sign_y*dy))

if points_from_1 & points_from_2:
    print('Yes')
else:
    print('No')
