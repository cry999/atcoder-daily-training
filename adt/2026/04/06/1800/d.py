N = int(input())

unauthorized = 0
state = "logout"
for _ in range(N):
    S = input()
    if S == "login" or S == "logout":
        state = S
    elif S == "public":
        pass
    else:  # S == 'private'
        unauthorized += state == "logout"

print(unauthorized)
