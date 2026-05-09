N, M, Q = map(int, input().split())
# users[n] := user n が見れるページのリスト
users = [set() for _ in range(N + 1)]
# power_users := 全てのページを見れる人
power_users = [False] * (N + 1)

for _ in range(Q):
    q, *args = map(int, input().split())

    if q == 1:
        x, y = args
        if power_users[x]:
            continue
        users[x].add(y)
        if len(users[x]) == M:
            power_users[x] = True

    elif q == 2:
        x = args[0]
        power_users[x] = True
    else:  # q == 3
        x, y = args
        if power_users[x]:
            print("Yes")
        elif y in users[x]:
            print("Yes")
        else:
            print("No")
