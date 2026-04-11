N = int(input())
S = input()

cx, cy = (0, 0)
visited = {(cx, cy)}

for c in S:
    if c == "R":
        cx += 1
    elif c == "L":
        cx -= 1
    elif c == "U":
        cy += 1
    else:
        cy -= 1

    if (cx, cy) in visited:
        print("Yes")
        break
    visited.add((cx, cy))
else:
    print("No")
