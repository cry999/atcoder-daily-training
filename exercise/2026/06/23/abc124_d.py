N, K = map(int, input().split())
S = input()

compress = []
for s in S:
    if not compress or compress[-1][0] != s:
        compress.append([s, 1])
    else:
        compress[-1][1] += 1

M = len(compress)
swap = 0
length = 0
ans = 0
head, tail = 0, 0
while head < M:
    tail = max(head, tail)
    while tail < M:
        s, cnt = compress[tail]
        if swap == K and s == "0":
            break
        if s == "0":
            swap += 1
        length += cnt
        tail += 1

    ans = max(ans, length)

    s, cnt = compress[head]
    if s == "0":
        swap -= 1
    length -= cnt
    head += 1
print(ans)
