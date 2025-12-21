N = int(input())

used = set()
while True:
    for i in range(1, 2*(N+1)):
        if i in used:
            continue
        used.add(i)
        print(i)
        break
    aoki = int(input())
    if aoki == 0:
        break
    used.add(aoki)
