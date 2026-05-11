Q = int(input())
playing = False
volume = 0

for _ in range(Q):
    A = int(input())
    if A == 1:
        volume += 1
    elif A == 2:
        volume = max(0, volume - 1)
    else:
        playing = not playing

    if volume >= 3 and playing:
        print("Yes")
    else:
        print("No")
