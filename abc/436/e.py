N = int(input())
*P, = map(int, input().split())

checked = [False] * N

ans = 0
for p in P:
    if checked[p-1]:
        continue

    cur = p
    cnt = 0
    while not checked[cur-1]:
        checked[cur-1] = True
        cur = P[cur-1]
        cnt += 1

    ans += cnt * (cnt-1) // 2

print(ans)
