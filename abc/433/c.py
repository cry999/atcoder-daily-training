S = input()

cur_and_num = []

cur = ('-2', 0)
for i, c in enumerate(S):
    # print(i, len(S)-1, c)
    p, cnt = cur
    if p == c:
        cur = (c, cnt+1)

    if p != c:
        # print('next')
        cur_and_num.append(cur)
        cur = (c, 1)

    if i == len(S)-1:
        # print('last')
        cur_and_num.append(cur)
        cur = (c, 1)


# print(cur_and_num)

ans = 0
for i in range(len(cur_and_num)-1):
    c1, cnt1 = cur_and_num[i]
    c2, cnt2 = cur_and_num[i+1]

    if int(c1)+1 == int(c2):
        ans += min(cnt1, cnt2)
print(ans)
