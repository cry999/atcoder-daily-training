from sortedcontainers import SortedList


N = int(input())
s = SortedList()
for _ in range(N):
    l, r = map(int, input().split())
    s.add((l, r))

ans = []
i = 0
while i < N:
    l, r = s[i]
    while i + 1 < N and s[i + 1][0] <= r:
        # 重なっている区間を繋げていく。
        i += 1
        r = max(s[i][1], r)

    ans.append((l, r))
    i += 1

for l, r in ans:
    print(l, r)
