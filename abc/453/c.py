N = int(input())
(*L,) = map(int, input().split())

ans = 0
for b in range(1 << N):
    cur = 0.5
    num = 0
    for i in range(N):
        if b & (1 << i):
            nxt = cur + L[i]
        else:
            nxt = cur - L[i]

        if nxt * cur < 0:
            num += 1
        cur = nxt

    ans = max(ans, num)

print(ans)
