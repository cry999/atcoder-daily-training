S = input()
K = int(input())

head, tail = 0, 0
dot_cnt = 0
ans = 0
while head < len(S) and tail < len(S):
    while tail < len(S):
        if dot_cnt == K and S[tail] == ".":
            break
        dot_cnt += S[tail] == "."
        tail += 1

    ans = max(ans, tail - head)

    if head == tail:
        head += 1
        tail += 1
        dot_cnt = 0
    else:
        while head < tail and S[head] == "X":
            head += 1
        if head < len(S) and S[head] == ".":
            head += 1
            dot_cnt -= 1

print(ans)
