X, Y = map(int, input().split())

steps = []
while X > 1 or Y > 1:
    steps.append((X, Y))
    if X > Y:
        X -= Y
    else:
        Y -= X

print(len(steps))
steps.reverse()
for x, y in steps:
    print(x, y)
