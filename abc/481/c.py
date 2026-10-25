Q = int(input())

account: dict[str, int] = {}
next_id = 1
for _ in range(Q):
    name = input()
    if name in account:
        print(account[name])
    else:
        account[name] = next_id
        next_id += 1
        print(account[name])
