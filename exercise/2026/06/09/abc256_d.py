N = int(input())
ranges = [tuple(map(int, input().split())) for _ in range(N)]
ranges.sort(reverse=True)

ans = []
while ranges:
    l0, r0 = ranges.pop()
    while ranges and ranges[-1][0] <= r0:
        _, r = ranges.pop()
        r0 = max(r0, r)

    ans.append((l0, r0))

for l, r in ans:
    print(l, r)
