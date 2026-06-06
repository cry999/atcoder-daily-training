from bisect import bisect_left

N = int(input())
slimes = sorted(tuple(map(int, input().split())) for _ in range(N))

ans = 0
for i in range(N):
    size, cnt = slimes[i]
    if cnt <= 1:
        # print("no power up", size, cnt)
        ans += cnt
        continue

    while cnt > 1:
        size *= 2
        nxt, cnt = divmod(cnt, 2)
        ans += cnt
        # print("power up", size, nxt, cnt)

        j = bisect_left(slimes, (size, 0), lo=i + 1)
        if j < N and slimes[j][0] == size:
            # print("found", size, slimes[j])
            _, c = slimes[j]
            nxt += c
            r = nxt % 2
            nxt -= r
            slimes[j] = (size, r)

        cnt = nxt
        # print("after power up", size, cnt)

    ans += cnt

print(ans)
