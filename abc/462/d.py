from sortedcontainers import SortedList

N, D = map(int, input().split())

suspects = SortedList([tuple(map(int, input().split())) for _ in range(N)])
in_the_house = SortedList()

ans = 0
for time in range(10**6 + 1):
    while in_the_house and in_the_house[0] < time + D:
        in_the_house.pop(0)

    while suspects and suspects[0][0] == time:
        entry, _exit = suspects.pop(0)
        if _exit - entry < D:
            continue
        in_the_house.add(_exit)

    if not in_the_house and not suspects:
        break
    n = len(in_the_house)
    ans += n * (n - 1) // 2


print(ans)
