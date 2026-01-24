Q = int(input())
volume = 0
playing = False

for _ in range(Q):
    a = int(input())
    if a == 1:
        volume += 1
    elif a == 2:
        volume = max(0, volume - 1)
    else:  # a == 3
        playing = not playing

    if volume >= 3 and playing:
        print("Yes")
    else:
        print("No")
