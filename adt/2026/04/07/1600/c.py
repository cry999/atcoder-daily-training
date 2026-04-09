N, K = map(int, input().split())
S = input()

head = 0
ans = 0
while head < N:
    while head < N and S[head] == "X":
        head += 1

    if head == N or head + K - 1 >= N:
        break

    if all(S[head + k] == "O" for k in range(K)):
        ans += 1
        head += K
    else:
        while head < N and S[head] == "O":
            head += 1

print(ans)
