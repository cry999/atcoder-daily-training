S = input()
K = int(input())


head, tail = 0, 0
dot_cnt = 0
ans = 0
while head < len(S):
    while tail < len(S):
        if S[tail] == "X":
            tail += 1
        elif dot_cnt + 1 <= K:
            tail += 1
            dot_cnt += 1
        else:
            # S[tail] == '.' and dot_cnt == K
            break

    ans = max(ans, tail - head)
    if S[head] == ".":
        dot_cnt -= 1
    head += 1
print(ans)
