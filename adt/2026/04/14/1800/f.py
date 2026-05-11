N = int(input())

cards = []
for i in range(N):
    a, c = map(int, input().split())
    cards.append((a, c, i))
cards.sort(reverse=True)

prev_st = float("inf")
prev_cost = float("inf")

ans = []
for s, c, i in cards:
    if prev_st > s:
        if prev_cost >= c:
            # ok
            prev_st = s
            prev_cost = c
        else:
            # ng
            continue
    elif prev_st == s:
        prev_cost = min(prev_cost, c)

    ans.append(i + 1)

ans.sort()
print(len(ans))
print(*ans)
