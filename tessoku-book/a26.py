Q = int(input())

for _ in range(Q):
    X = int(input())

    if X in (2, 3, 5, 7, 11):
        print('Yes')
        continue
    if X == 1:
        print('No')
        continue
    if X % 2 == 0 or X % 3 == 0 or X % 5 == 0 or X % 7 == 0 or X % 11 == 0:
        print('No')
        continue

    i = 13
    while i * i <= X:
        if X % i == 0:
            print('No')
            break
        i += 2
    else:
        print('Yes')
